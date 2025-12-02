"""
Azure AI Search integration for knowledge base retrieval
"""
import logging
from typing import List, Optional, Dict, Any

try:
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient
    from azure.search.documents.models import VectorizedQuery
    SEARCH_AVAILABLE = True
except ImportError:
    SEARCH_AVAILABLE = False
    SearchClient = None
    AzureKeyCredential = None
    VectorizedQuery = None

from ..config.settings import settings
from ..models.schemas import KnowledgeArticle, TicketCategory

logger = logging.getLogger(__name__)


class KnowledgeBaseService:
    """
    Knowledge base service using Azure AI Search
    """
    
    def __init__(self):
        self.client: Optional[SearchClient] = None
        self._initialize_client()
        self._initialize_mock_data()
        
    def _initialize_client(self):
        """Initialize Azure AI Search client"""
        if not SEARCH_AVAILABLE:
            logger.warning("Azure Search SDK not installed, running in fallback mode")
            return
            
        if not settings.AZURE_SEARCH_ENDPOINT or not settings.AZURE_SEARCH_KEY:
            logger.warning("Azure Search credentials not found, running in fallback mode")
            return
            
        if settings.AZURE_SEARCH_ENDPOINT and settings.AZURE_SEARCH_KEY:
            try:
                credential = AzureKeyCredential(settings.AZURE_SEARCH_KEY)
                self.client = SearchClient(
                    endpoint=settings.AZURE_SEARCH_ENDPOINT,
                    index_name=settings.AZURE_SEARCH_INDEX_NAME,
                    credential=credential
                )
                logger.info("Azure AI Search client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Azure AI Search: {e}")

    def _initialize_mock_data(self):
        """Initialize rich mock data for development"""
        self.mock_articles = []
        
        # IT Support Articles
        self.mock_articles.extend([
            KnowledgeArticle(
                id="it-001", category=TicketCategory.IT_SUPPORT, title="Password Reset Policy & Procedure",
                content="To reset your password: 1. Go to https://password.company.com 2. Click 'Forgot Password'. If you are locked out, contact the Service Desk at x1234. Passwords must be 12 characters long.",
                tags=["password", "reset", "login", "access", "contraseña", "olvidé", "resetear", "clave"], source="Internal Wiki"
            ),
            KnowledgeArticle(
                id="it-009", category=TicketCategory.IT_SUPPORT, title="Account Lockout Procedures",
                content="If your account is locked due to multiple failed attempts, wait 15 minutes for auto-unlock. For immediate unlock, call the Service Desk. Do not share your password.",
                tags=["lockout", "account", "login", "blocked", "bloqueado", "cuenta", "acceso"], source="Security Policy"
            ),
            KnowledgeArticle(
                id="it-002", category=TicketCategory.IT_SUPPORT, title="VPN Connection Troubleshooting",
                content="If VPN fails to connect: 1. Check internet connection. 2. Restart Cisco AnyConnect. 3. Verify certificate validity. 4. Contact IT if error 'Host Unreachable' persists.",
                tags=["vpn", "connection", "network", "remote", "cisco", "internet", "red", "conexión"], source="IT Knowledge Base"
            ),
            KnowledgeArticle(
                id="it-003", category=TicketCategory.IT_SUPPORT, title="Requesting New Software",
                content="To request new software: Submit a ticket via the Service Portal with business justification and manager approval. Standard software (Office, Adobe Reader) is auto-approved.",
                tags=["software", "install", "request", "application", "program", "instalar", "programa"], source="Service Portal"
            ),
            KnowledgeArticle(
                id="it-004", category=TicketCategory.IT_SUPPORT, title="Printer Setup Guide",
                content="Add a printer: Settings > Devices > Printers & Scanners > Add a printer. Select 'Search Directory' to find office printers by location code (e.g., NY-FL3).",
                tags=["printer", "print", "setup", "driver", "impresora", "imprimir", "configurar"], source="IT Guides"
            ),
            KnowledgeArticle(
                id="it-005", category=TicketCategory.IT_SUPPORT, title="Email Configuration for Mobile",
                content="Download Outlook app. Enter your company email. It will redirect to SSO login. Approve MFA prompt. Do not use native mail apps for security reasons.",
                tags=["email", "outlook", "mobile", "phone", "ios", "android", "correo", "celular"], source="Mobile Device Management"
            ),
            KnowledgeArticle(
                id="it-006", category=TicketCategory.IT_SUPPORT, title="Reporting Phishing Emails",
                content="Use the 'Report Phishing' button in Outlook ribbon. Do not click links or download attachments. If you clicked something, call Security immediately at x9999.",
                tags=["phishing", "security", "email", "spam", "virus", "seguridad", "estafa"], source="Security Policy"
            ),
            KnowledgeArticle(
                id="it-007", category=TicketCategory.IT_SUPPORT, title="Wi-Fi Access for Guests",
                content="Guest Wi-Fi network is 'Company-Guest'. Password rotates weekly and is displayed at reception. Employees must use 'Company-Secure' with their credentials.",
                tags=["wifi", "internet", "network", "guest", "wireless", "invitado", "clave"], source="Network Policy"
            ),
            KnowledgeArticle(
                id="it-008", category=TicketCategory.IT_SUPPORT, title="Laptop Refresh Cycle",
                content="Standard laptop refresh cycle is 3 years. You will receive an email 30 days before eligibility to choose a new model (Windows or Mac).",
                tags=["laptop", "computer", "hardware", "upgrade", "refresh", "computadora", "equipo"], source="Asset Management"
            ),
            KnowledgeArticle(
                id="it-009", category=TicketCategory.IT_SUPPORT, title="Accessing Shared Drives",
                content="Map network drive: File Explorer > This PC > Map network drive. Path: \\\\fileserver\\department. Request access via ticket if 'Access Denied'.",
                tags=["drive", "shared", "files", "folder", "server", "archivos", "carpeta"], source="IT Knowledge Base"
            ),
            KnowledgeArticle(
                id="it-010", category=TicketCategory.IT_SUPPORT, title="Monitor Troubleshooting",
                content="If monitor is black: Check power cable. Check HDMI/DisplayPort connection. Try a different cable. If using a dock, update dock firmware.",
                tags=["monitor", "screen", "display", "hardware", "pantalla", "cable"], source="Hardware Support"
            )
        ])

        # HR Inquiry Articles
        self.mock_articles.extend([
            KnowledgeArticle(
                id="hr-001", category=TicketCategory.HR_INQUIRY, title="How to Check Your Leave Balance",
                content="Log in to the HR Portal: https://hr.company.com > 'My Profile' > 'Leave & Time Off'. You can verify your vacation days, sick leave, and personal time off.",
                tags=["leave", "vacation", "time off", "holiday", "vacaciones", "días libres"], source="HR Portal"
            ),
            KnowledgeArticle(
                id="hr-002", category=TicketCategory.HR_INQUIRY, title="Updating Direct Deposit Info",
                content="Go to Workday > Pay > Payment Elections. You can add or edit bank accounts. Changes take 1-2 pay cycles to process.",
                tags=["payroll", "bank", "deposit", "salary", "account", "banco", "sueldo", "pago"], source="Payroll Guide"
            ),
            KnowledgeArticle(
                id="hr-003", category=TicketCategory.HR_INQUIRY, title="Health Insurance Enrollment",
                content="Open enrollment is in November. New hires have 30 days to enroll via the Benefits Portal. Qualifying life events (marriage, birth) allow mid-year changes.",
                tags=["insurance", "health", "benefits", "medical", "dental", "seguro", "salud", "beneficios"], source="Benefits Handbook"
            ),
            KnowledgeArticle(
                id="hr-004", category=TicketCategory.HR_INQUIRY, title="Reporting Harassment",
                content="We have a zero-tolerance policy. Report incidents to your HRBP or anonymously via the Ethics Hotline (1-800-ETHICS). All reports are investigated confidentially.",
                tags=["harassment", "ethics", "report", "policy", "conduct", "denuncia", "ética"], source="Employee Handbook"
            ),
            KnowledgeArticle(
                id="hr-005", category=TicketCategory.HR_INQUIRY, title="Performance Review Process",
                content="Reviews occur bi-annually (Mid-year in July, End-year in January). Self-evaluation is required in Workday before manager review.",
                tags=["performance", "review", "evaluation", "feedback", "career", "evaluación", "desempeño"], source="Talent Management"
            ),
            KnowledgeArticle(
                id="hr-006", category=TicketCategory.HR_INQUIRY, title="Parental Leave Policy",
                content="The company offers 12 weeks of paid parental leave for primary caregivers and 4 weeks for secondary caregivers. Apply via Leave Administrator.",
                tags=["parental", "leave", "maternity", "paternity", "baby", "licencia", "maternidad"], source="Benefits Policy"
            ),
            KnowledgeArticle(
                id="hr-007", category=TicketCategory.HR_INQUIRY, title="Tuition Reimbursement",
                content="Full-time employees are eligible for up to $5,000/year for degree-related courses. Pre-approval required. Must maintain 'B' grade or higher.",
                tags=["tuition", "education", "reimbursement", "study", "degree", "estudio", "universidad"], source="L&D Policy"
            ),
            KnowledgeArticle(
                id="hr-008", category=TicketCategory.HR_INQUIRY, title="401(k) Matching",
                content="The company matches 50% of your contribution up to 6% of your salary. Vesting period is 3 years. Manage contributions at Fidelity NetBenefits.",
                tags=["401k", "retirement", "pension", "investing", "finance", "jubilación", "retiro"], source="Benefits Guide"
            ),
            KnowledgeArticle(
                id="hr-009", category=TicketCategory.HR_INQUIRY, title="Resignation Procedure",
                content="Submit formal resignation letter to your manager and HRBP. Standard notice period is 2 weeks. Exit interview will be scheduled on your last day.",
                tags=["resignation", "quit", "notice", "exit", "leaving", "renuncia", "salida"], source="HR Policy"
            ),
            KnowledgeArticle(
                id="hr-010", category=TicketCategory.HR_INQUIRY, title="Employee Referral Program",
                content="Refer a candidate via the Career Portal. If hired, you receive a bonus ($1000 for standard, $2000 for tech roles) after they complete 90 days.",
                tags=["referral", "bonus", "hiring", "recruitment", "jobs", "referido", "bono"], source="Recruiting"
            )
        ])

        # Finance Articles
        self.mock_articles.extend([
            KnowledgeArticle(
                id="fin-001", category=TicketCategory.FINANCE, title="Submitting Expense Reports",
                content="Use Concur for all expenses. Receipts required for items over $25. Submit by the 5th of the month for reimbursement in the next cycle.",
                tags=["expense", "report", "concur", "reimbursement", "money", "gastos", "reembolso"], source="Finance Policy"
            ),
            KnowledgeArticle(
                id="fin-002", category=TicketCategory.FINANCE, title="Corporate Credit Card Policy",
                content="Corporate cards are for business travel and client entertainment only. Personal use is strictly prohibited. Lost cards must be reported immediately.",
                tags=["credit card", "corporate", "card", "policy", "spending", "tarjeta", "crédito"], source="Travel & Expense"
            ),
            KnowledgeArticle(
                id="fin-003", category=TicketCategory.FINANCE, title="Invoice Processing",
                content="Send vendor invoices to accounts.payable@company.com. Include PO number. Standard payment terms are Net 45.",
                tags=["invoice", "payment", "vendor", "ap", "accounts payable", "factura", "pago"], source="AP Guide"
            ),
            KnowledgeArticle(
                id="fin-004", category=TicketCategory.FINANCE, title="Budget Request Process",
                content="Annual budget planning starts in October. Out-of-cycle budget requests require CFO approval using the 'Budget Variance Form'.",
                tags=["budget", "planning", "finance", "approval", "money", "presupuesto"], source="FP&A"
            ),
            KnowledgeArticle(
                id="fin-005", category=TicketCategory.FINANCE, title="Payroll Discrepancies",
                content="If your paycheck is incorrect, open a ticket with 'Payroll' category immediately. Attach paystub and highlight the error.",
                tags=["payroll", "salary", "paycheck", "error", "money", "nómina", "sueldo"], source="Payroll Support"
            ),
            KnowledgeArticle(
                id="fin-006", category=TicketCategory.FINANCE, title="Travel Allowance Rates",
                content="Daily per diem for meals is $75 (domestic) and $100 (international). Hotel cap varies by city. See the 'Travel Rate Card 2024' for details.",
                tags=["travel", "allowance", "per diem", "meals", "hotel", "viaje", "viáticos"], source="Travel Policy"
            ),
            KnowledgeArticle(
                id="fin-007", category=TicketCategory.FINANCE, title="Procurement Policy",
                content="Purchases over $5,000 require 3 competitive bids. Use the 'Procurement Portal' to initiate an RFP (Request for Proposal).",
                tags=["procurement", "purchasing", "buying", "bids", "rfp", "compras", "proveedores"], source="Procurement"
            ),
            KnowledgeArticle(
                id="fin-008", category=TicketCategory.FINANCE, title="Tax Documents (W-2)",
                content="W-2 forms are available in ADP by Jan 31st. Physical copies are mailed to your home address on file.",
                tags=["tax", "w2", "documents", "irs", "impuestos"], source="Payroll"
            ),
            KnowledgeArticle(
                id="fin-009", category=TicketCategory.FINANCE, title="Client Billing Inquiries",
                content="For questions about client invoices, contact the AR team at accounts.receivable@company.com with the Invoice ID.",
                tags=["billing", "client", "invoice", "ar", "accounts receivable", "facturación", "cobranzas"], source="AR Team"
            ),
            KnowledgeArticle(
                id="fin-010", category=TicketCategory.FINANCE, title="Petty Cash Policy",
                content="Petty cash is for small office supplies under $50. Keep receipts in the lockbox. Reconcile monthly with the Office Manager.",
                tags=["cash", "petty", "money", "supplies", "caja chica"], source="Finance Ops"
            )
        ])

        # Facilities Articles
        self.mock_articles.extend([
            KnowledgeArticle(
                id="fac-001", category=TicketCategory.FACILITIES, title="Office Access Cards",
                content="Lost badges must be reported to Security immediately. Replacement fee is $20. New badges can be picked up at Reception 9am-5pm.",
                tags=["badge", "access", "card", "security", "entry", "tarjeta", "acceso"], source="Security"
            ),
            KnowledgeArticle(
                id="fac-002", category=TicketCategory.FACILITIES, title="Meeting Room Booking",
                content="Book rooms via Outlook Calendar or the Room Panel. If you do not check in within 10 mins, the room is released. Clean up after use.",
                tags=["room", "meeting", "booking", "calendar", "conference", "sala", "reunión"], source="Office Management"
            ),
            KnowledgeArticle(
                id="fac-003", category=TicketCategory.FACILITIES, title="HVAC / Temperature Request",
                content="Standard office temperature is set to 72°F (22°C). To request adjustment, submit a Facilities ticket with your zone/desk number.",
                tags=["temperature", "ac", "heat", "cold", "hvac", "office", "aire", "calefacción"], source="Building Ops"
            ),
            KnowledgeArticle(
                id="fac-004", category=TicketCategory.FACILITIES, title="Visitor Policy",
                content="All visitors must be pre-registered in the Envoy system. They must sign an NDA at reception and be escorted at all times.",
                tags=["visitor", "guest", "policy", "entry", "visita", "invitado"], source="Security"
            ),
            KnowledgeArticle(
                id="fac-005", category=TicketCategory.FACILITIES, title="Parking Permits",
                content="Monthly parking passes are available for $100/month (deducted from payroll). Submit vehicle details to Facilities to receive your tag.",
                tags=["parking", "car", "garage", "permit", "estacionamiento", "auto"], source="Facilities"
            ),
            KnowledgeArticle(
                id="fac-006", category=TicketCategory.FACILITIES, title="Janitorial Services",
                content="Cleaning happens nightly. For spills or urgent cleaning, call x5555. Do not leave food in the fridge over the weekend.",
                tags=["cleaning", "janitor", "trash", "spill", "limpieza", "basura"], source="Building Ops"
            ),
            KnowledgeArticle(
                id="fac-007", category=TicketCategory.FACILITIES, title="Mail and Packages",
                content="Personal packages should not be delivered to the office. Business mail is sorted by 10am daily in the mailroom.",
                tags=["mail", "package", "delivery", "post", "correo", "paquete"], source="Mailroom"
            ),
            KnowledgeArticle(
                id="fac-008", category=TicketCategory.FACILITIES, title="Ergonomic Assessments",
                content="Request an ergonomic assessment if you experience discomfort. We provide standing desks, ergonomic chairs, and monitor arms upon recommendation.",
                tags=["ergonomic", "desk", "chair", "health", "back pain", "silla", "escritorio"], source="H&S"
            ),
            KnowledgeArticle(
                id="fac-009", category=TicketCategory.FACILITIES, title="Emergency Evacuation",
                content="In case of fire alarm, use the stairs (NOT elevators). Assemble at the designated point in the parking lot. Fire wardens wear orange vests.",
                tags=["fire", "emergency", "evacuation", "safety", "alarm", "incendio", "emergencia"], source="Safety"
            ),
            KnowledgeArticle(
                id="fac-010", category=TicketCategory.FACILITIES, title="Gym Access",
                content="The office gym is open 6am-8pm. Waiver must be signed. Showers and lockers are available. Bring your own towel.",
                tags=["gym", "fitness", "workout", "health", "gimnasio"], source="Employee Perks"
            )
        ])

        # Legal Articles
        self.mock_articles.extend([
            KnowledgeArticle(
                id="leg-001", category=TicketCategory.LEGAL, title="NDA Request Process",
                content="Use the 'Standard Mutual NDA' template for most vendors. For custom NDAs, submit a Legal Request ticket. Turnaround time is 3 business days.",
                tags=["nda", "contract", "confidentiality", "agreement", "legal", "contrato"], source="Legal Portal"
            ),
            KnowledgeArticle(
                id="leg-002", category=TicketCategory.LEGAL, title="Contract Review Policy",
                content="All contracts over $10k or with IP implications must be reviewed by Legal. Do not sign anything without approval.",
                tags=["contract", "review", "sign", "agreement", "policy", "contrato", "firma"], source="Legal Policy"
            ),
            KnowledgeArticle(
                id="leg-003", category=TicketCategory.LEGAL, title="Data Privacy (GDPR/CCPA)",
                content="Report any potential data breach immediately to the DPO (dpo@company.com). Customer data deletion requests must be processed within 30 days.",
                tags=["privacy", "data", "gdpr", "ccpa", "compliance", "privacidad", "datos"], source="Compliance"
            ),
            KnowledgeArticle(
                id="leg-004", category=TicketCategory.LEGAL, title="Intellectual Property",
                content="All code, designs, and content created during work hours are property of the company. Moonlighting requires disclosure.",
                tags=["ip", "intellectual property", "copyright", "ownership", "propiedad intelectual"], source="Legal Handbook"
            ),
            KnowledgeArticle(
                id="leg-005", category=TicketCategory.LEGAL, title="Conflict of Interest",
                content="Employees must disclose any outside business interests or relationships that could conflict with company duties via the Conflict of Interest form.",
                tags=["conflict", "interest", "disclosure", "ethics", "conflicto"], source="Compliance"
            ),
            KnowledgeArticle(
                id="leg-006", category=TicketCategory.LEGAL, title="Whistleblower Policy",
                content="Employees are protected from retaliation when reporting illegal or unethical activities. Reports can be made anonymously.",
                tags=["whistleblower", "report", "illegal", "unethical", "protection", "denuncia"], source="Compliance"
            ),
            KnowledgeArticle(
                id="leg-007", category=TicketCategory.LEGAL, title="Social Media Policy",
                content="Do not post confidential company info. Make it clear that opinions are your own. Do not engage with media inquiries; refer them to PR.",
                tags=["social media", "policy", "facebook", "twitter", "linkedin", "redes sociales"], source="Comms Policy"
            ),
            KnowledgeArticle(
                id="leg-008", category=TicketCategory.LEGAL, title="Document Retention",
                content="Financial records must be kept for 7 years. Contracts for 10 years. Emails are auto-archived for 5 years.",
                tags=["retention", "document", "record", "archive", "storage", "archivo"], source="Legal Ops"
            ),
            KnowledgeArticle(
                id="leg-009", category=TicketCategory.LEGAL, title="Immigration Support",
                content="The company sponsors H1-B and Green Cards for eligible roles. Contact immigration@company.com for eligibility assessment.",
                tags=["immigration", "visa", "sponsorship", "h1b", "green card", "inmigración"], source="HR/Legal"
            ),
            KnowledgeArticle(
                id="leg-010", category=TicketCategory.LEGAL, title="Signature Authority",
                content="Only VP level and above have signature authority for contracts. Directors can sign up to $50k. Managers cannot sign contracts.",
                tags=["signature", "authority", "sign", "power", "firma"], source="Corporate Governance"
            ),
            KnowledgeArticle(
                id="hr-005", category=TicketCategory.HR_INQUIRY, title="Obra Social y Beneficios de Salud",
                content="Para dar de alta a familiares (cónyuge, hijos) en la obra social, debe completar el formulario F-102 en el Portal de RRHH y adjuntar certificado de matrimonio/convivencia o partida de nacimiento. El trámite demora 48hs.",
                tags=["obra social", "salud", "alta", "pareja", "hijos", "beneficios", "health insurance", "spouse"], source="HR Benefits"
            )
        ])

    async def search(self, query: str, category: Optional[str] = None, limit: int = 3) -> List[KnowledgeArticle]:
        """
        Search knowledge base using Azure AI Search
        """
        logger.info(f"Searching KB with query='{query}', category='{category}'")
        if not self.client:
            return self._mock_search(query, category, limit)
            
        try:
            # Build filter
            filter_expression = None
            if category:
                filter_expression = f"category eq '{category}'"
                
            # Execute search
            results = self.client.search(
                search_text=query,
                filter=filter_expression,
                top=limit,
                include_total_count=True
            )
            
            articles = []
            for result in results:
                articles.append(KnowledgeArticle(
                    id=result.get("id", ""),
                    category=result.get("category", TicketCategory.UNKNOWN),
                    title=result.get("title", ""),
                    content=result.get("content", ""),
                    tags=result.get("keywords", []),
                    source=result.get("url", "Azure Search")
                ))
                
            return articles
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return self._mock_search(query, category, limit)

    def _mock_search(self, query: str, category: Optional[str] = None, limit: int = 3) -> List[KnowledgeArticle]:
        """Fallback in-memory search for development"""
        
        results = []
        query_lower = query.lower()
        
        for article in self.mock_articles:
            if category and article.category != category:
                continue
            
            # Token-based matching for natural language queries
            query_tokens = set(query_lower.split())
            
            score = 0
            # Title match (high weight)
            if query_lower in article.title.lower():
                score += 10
            else:
                title_tokens = set(article.title.lower().split())
                common_title = query_tokens.intersection(title_tokens)
                score += len(common_title) * 3
            
            # Content match (medium weight)
            if query_lower in article.content.lower():
                score += 5
            else:
                content_tokens = set(article.content.lower().split())
                common_content = query_tokens.intersection(content_tokens)
                score += len(common_content) * 1
                
            # Keyword match
            for keyword in article.tags:
                keyword_lower = keyword.lower()
                if keyword_lower in query_lower:
                    score += 5
                elif keyword_lower in query_tokens:
                    score += 5
            
            if score > 2:
                # Add score attribute dynamically for sorting
                article.relevance_score = score
                results.append(article)
                
        # Sort by score
        results.sort(key=lambda x: getattr(x, 'relevance_score', 0), reverse=True)
        
        # If we don't have enough results, fill with other articles from the same category
        # DISABLED: Do not return random articles if no match found
        # if len(results) < limit and category:
        #     existing_ids = {r.id for r in results}
        #     for article in self.mock_articles:
        #         if len(results) >= limit:
        #             break
        #         if article.category == category and article.id not in existing_ids:
        #             results.append(article)
                    
        return results[:limit]

    async def get_all_articles(self) -> List[KnowledgeArticle]:
        """Get all articles (mock implementation)"""
        return self.mock_articles

    async def get_article(self, article_id: str) -> Optional[KnowledgeArticle]:
        """Get article by ID"""
        for article in self.mock_articles:
            if article.id == article_id:
                return article
        return None

    async def create_article(self, article: Any) -> KnowledgeArticle:
        """Create new article (mock)"""
        new_article = KnowledgeArticle(
            id=f"new-{len(self.mock_articles) + 1}",
            category=article.category,
            title=article.title,
            content=article.content,
            tags=article.tags,
            source=article.source
        )
        self.mock_articles.append(new_article)
        return new_article

    async def update_article(self, article_id: str, article_update: Any) -> Optional[KnowledgeArticle]:
        """Update article (mock)"""
        existing = await self.get_article(article_id)
        if not existing:
            return None
        
        # Update fields if provided
        if article_update.title: existing.title = article_update.title
        if article_update.content: existing.content = article_update.content
        if article_update.category: existing.category = article_update.category
        if article_update.tags: existing.tags = article_update.tags
        if article_update.source: existing.source = article_update.source
        
        return existing

    async def delete_article(self, article_id: str) -> bool:
        """Delete article (mock)"""
        for i, article in enumerate(self.mock_articles):
            if article.id == article_id:
                self.mock_articles.pop(i)
                return True
        return False

# Singleton instance
_kb_service = None

def get_knowledge_base() -> KnowledgeBaseService:
    """Get singleton knowledge base instance"""
    global _kb_service
    if _kb_service is None:
        _kb_service = KnowledgeBaseService()
    return _kb_service
