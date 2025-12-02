import logging
import base64
import io
from typing import Optional
from openai import AsyncAzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from ..config.settings import settings
import pypdf
import docx

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self):
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        try:
            if settings.AZURE_OPENAI_API_KEY:
                self.client = AsyncAzureOpenAI(
                    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                    api_key=settings.AZURE_OPENAI_API_KEY,
                    api_version="2024-02-15-preview"
                )
            else:
                # Use Managed Identity
                token_provider = get_bearer_token_provider(
                    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
                )
                self.client = AsyncAzureOpenAI(
                    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                    azure_ad_token_provider=token_provider,
                    api_version="2024-02-15-preview"
                )
            logger.info("DocumentService: Azure OpenAI client initialized")
        except Exception as e:
            logger.error(f"DocumentService: Failed to initialize Azure OpenAI client: {e}")

    async def process_file(self, file_content: bytes, filename: str) -> str:
        """
        Process file based on extension:
        - Images: OCR via GPT-4o Vision
        - PDF: Text extraction via pypdf
        - Word: Text extraction via python-docx
        
        Returns: Summary + Full Text
        """
        if not self.client:
            return "[Error] Document Service unavailable."

        ext = filename.lower().split('.')[-1]
        extracted_text = ""

        try:
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                extracted_text = await self._extract_image_text(file_content, ext)
            elif ext == 'pdf':
                extracted_text = self._extract_pdf_text(file_content)
            elif ext in ['docx', 'doc']:
                extracted_text = self._extract_docx_text(file_content)
            else:
                return f"Unsupported file type: {ext}"

            if not extracted_text.strip():
                return "No text detected in document."

            # Generate Summary
            summary = await self._summarize_text(extracted_text)
            
            return f"**Document Summary:**\n{summary}\n\n---\n**Extracted Content:**\n{extracted_text}"

        except Exception as e:
            logger.error(f"Error processing file {filename}: {e}", exc_info=True)
            return f"Error processing file: {str(e)}"

    async def _extract_image_text(self, file_content: bytes, ext: str) -> str:
        """Extract text from image using GPT-4o Vision"""
        base64_image = base64.b64encode(file_content).decode('utf-8')
        mime_type = f"image/{ext}" if ext != 'jpg' else "image/jpeg"
        
        response = await self.client.chat.completions.create(
            model=settings.AZURE_OPENAI_GPT4O_DEPLOYMENT,
            messages=[
                {
                    "role": "system",
                    "content": "You are an OCR assistant. Extract all text from the provided image. Return ONLY the extracted text."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract text from this image:"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=2000
        )
        return response.choices[0].message.content

    def _extract_pdf_text(self, file_content: bytes) -> str:
        """Extract text from PDF using pypdf"""
        text = ""
        try:
            pdf_file = io.BytesIO(file_content)
            reader = pypdf.PdfReader(pdf_file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"PDF Extraction failed: {e}")
            raise
        return text

    def _extract_docx_text(self, file_content: bytes) -> str:
        """Extract text from DOCX using python-docx"""
        text = ""
        try:
            docx_file = io.BytesIO(file_content)
            doc = docx.Document(docx_file)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            logger.error(f"DOCX Extraction failed: {e}")
            raise
        return text

    async def _summarize_text(self, text: str) -> str:
        """Summarize text using GPT-4o"""
        # Truncate if too long for context window (approx check)
        if len(text) > 100000:
            text = text[:100000] + "... [truncated]"

        response = await self.client.chat.completions.create(
            model=settings.AZURE_OPENAI_GPT4O_DEPLOYMENT,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Summarize the following document content concisely. Identify key queries, issues, or topics mentioned."
                },
                {
                    "role": "user",
                    "content": f"Summarize this content:\n\n{text}"
                }
            ],
            max_tokens=500
        )
        return response.choices[0].message.content
