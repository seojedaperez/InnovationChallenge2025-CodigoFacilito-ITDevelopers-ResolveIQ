import React, { useEffect, useState } from 'react';
import {
    Text,
    makeStyles,
    shorthands,
    Button,
    Spinner,
    Dialog,
    DialogSurface,
    DialogBody,
    DialogTitle,
    DialogContent
} from '@fluentui/react-components';
import { BookOpen24Regular, ChevronRight24Regular } from '@fluentui/react-icons';
import axios from 'axios';
import { useMsal } from "@azure/msal-react";
import { loginRequest } from '../authConfig';

import { useSettings } from '../context/SettingsContext';

const useStyles = makeStyles({
    container: {
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
        marginTop: 'auto',
        paddingTop: '15px',
        borderTop: '1px solid rgba(255, 255, 255, 0.1)',
        maxHeight: '250px', // Fixed height to ensure it fits
        overflowY: 'auto', // Enable internal scrolling
        paddingRight: '5px', // Space for scrollbar
        // Custom scrollbar styling
        '&::-webkit-scrollbar': {
            width: '8px',
        },
        '&::-webkit-scrollbar-track': {
            background: 'rgba(255, 255, 255, 0.05)',
            borderRadius: '4px',
        },
        '&::-webkit-scrollbar-thumb': {
            background: 'rgba(255, 255, 255, 0.2)',
            borderRadius: '4px',
            ':hover': {
                background: 'rgba(255, 255, 255, 0.3)',
            },
        },
    },
    articleCard: {
        backgroundColor: 'rgba(255, 255, 255, 0.03)',
        ...shorthands.padding('12px'),
        borderRadius: '12px',
        cursor: 'pointer',
        border: '1px solid rgba(255, 255, 255, 0.05)',
        transition: 'all 0.2s ease',
        ':hover': {
            backgroundColor: 'rgba(255, 255, 255, 0.08)',
            transform: 'translateX(4px)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
        }
    }
});

interface KBArticle {
    id: string;
    title: string;
    content: string;
    category: string;
    relevance_score?: number;
}

interface RelatedArticlesProps {
    query: string;
    language?: string;
    onArticleClick?: (article: KBArticle) => void;
}

export const RelatedArticles: React.FC<RelatedArticlesProps> = ({ query, language = 'en', onArticleClick }) => {
    const styles = useStyles();
    const { t, accessibility } = useSettings();
    const { instance, accounts } = useMsal();
    const [articles, setArticles] = useState<KBArticle[]>([]);
    const [loading, setLoading] = useState(false);
    const [selectedArticle, setSelectedArticle] = useState<KBArticle | null>(null);

    useEffect(() => {
        if (!query || query.length < 3) return;

        const fetchArticles = async () => {
            setLoading(true);
            try {
                const account = accounts[0];
                let accessToken = "dummy-dev-token";
                if (account) {
                    try {
                        const response = await instance.acquireTokenSilent({
                            ...loginRequest,
                            account
                        });
                        accessToken = response.accessToken;
                    } catch (e) {
                        console.warn("Token silent acquisition failed", e);
                    }
                }

                const response = await axios.get('/api/v1/knowledge/search', {
                    params: { query, limit: 3, language },
                    headers: { 'Authorization': `Bearer ${accessToken}` }
                });

                // Deduplicate articles based on ID to prevent duplicate key errors
                const uniqueArticles = Array.from(new Map(response.data.results.map((item: KBArticle) => [item.id, item])).values());
                setArticles(uniqueArticles as KBArticle[]);
            } catch (error) {
                console.error('Error fetching related articles:', error);
            } finally {
                setLoading(false);
            }
        };

        const debounce = setTimeout(fetchArticles, 500);
        return () => clearTimeout(debounce);
    }, [query, language, instance, accounts]);

    if (!query) return null;

    if (articles.length === 0 && !loading) {
        return null;
    }

    return (
        <>
            <div className={styles.container}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '5px' }}>
                    <BookOpen24Regular style={{ color: 'var(--primary-neon)' }} />
                    <Text weight="semibold" style={{
                        fontSize: accessibility.wcagLevel === 'AAA' ? '18px' : accessibility.wcagLevel === 'AA' ? '16px' : '14px'
                    }}>
                        {t('Related Knowledge Base Articles')}
                    </Text>
                    {loading && <Spinner size="tiny" />}
                </div>

                {articles.map(article => (
                    <div
                        key={article.id}
                        className={styles.articleCard}
                        onClick={() => onArticleClick?.(article)}
                    >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Text weight="medium" style={{
                                fontSize: accessibility.wcagLevel === 'AAA' ? '16px' : accessibility.wcagLevel === 'AA' ? '14px' : '13px'
                            }}>
                                {article.title}
                            </Text>
                            <ChevronRight24Regular style={{ fontSize: '16px', color: 'var(--text-muted)' }} />
                        </div>
                        <Text size={200} style={{
                            color: 'var(--text-muted)',
                            fontSize: accessibility.wcagLevel === 'AAA' ? '14px' : accessibility.wcagLevel === 'AA' ? '12px' : '11px'
                        }} className="text-clamp-2">
                            {article.content}
                        </Text>
                        <div style={{ marginTop: '8px', display: 'flex', justifyContent: 'flex-end' }}>
                            <Button
                                size="small"
                                appearance="secondary"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    setSelectedArticle(article);
                                }}
                            >{
                                    t('View Article')}
                            </Button>
                        </div>
                    </div>
                ))}
            </div>

            {selectedArticle && (
                <Dialog open={!!selectedArticle} onOpenChange={() => setSelectedArticle(null)}>
                    <DialogSurface style={{ maxWidth: '600px', width: '90%' }}>
                        <DialogBody>
                            <DialogTitle
                                action={
                                    <Button appearance="subtle" aria-label="close" onClick={() => setSelectedArticle(null)}>{t('Close')}</Button>
                                }
                            >
                                {selectedArticle.title}
                            </DialogTitle>
                            <DialogContent>
                                <div style={{ lineHeight: '1.6', color: 'var(--text-primary)', whiteSpace: 'pre-wrap' }}>
                                    {selectedArticle.content}
                                </div>
                            </DialogContent>
                        </DialogBody>
                    </DialogSurface>
                </Dialog>
            )}
        </>
    );
};
