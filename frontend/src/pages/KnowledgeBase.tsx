import React, { useState, useEffect } from 'react';
import {
    Text,
    Input,
    Button,
    makeStyles,
    shorthands,
    Card,
    CardHeader,
    Spinner,
    Badge,
    Dialog,
    DialogSurface,
    DialogBody,
    DialogTitle,
    DialogContent,
    DialogActions,
    Label,
    Textarea,
    Dropdown,
    Option,
    useId
} from '@fluentui/react-components';
import {
    Search24Regular,
    BookOpen24Regular,
    Add24Regular,
    Edit24Regular,
    Delete24Regular
} from '@fluentui/react-icons';
import axios from 'axios';
import { useMsal } from "@azure/msal-react";
import { loginRequest } from '../authConfig';
import { useSettings } from '../context/SettingsContext';

const useStyles = makeStyles({
    container: {
        display: 'flex',
        flexDirection: 'column',
        gap: '20px',
        height: '100%',
        ...shorthands.padding('20px'),
        overflowY: 'auto'
    },
    header: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '20px',
    },
    searchContainer: {
        display: 'flex',
        gap: '10px',
        backgroundColor: 'var(--bg-card)',
        ...shorthands.padding('10px'),
        borderRadius: '12px',
        border: 'var(--glass-border)',
        alignItems: 'center',
        boxSizing: 'border-box',
        width: '100%',
    },
    resultsGrid: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '20px',
    },
    articleCard: {
        backgroundColor: 'var(--bg-card)',
        border: 'var(--glass-border)',
        borderRadius: '12px',
        cursor: 'pointer',
        transition: 'transform 0.2s, box-shadow 0.2s',
        ':hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 8px 20px rgba(0,0,0,0.3)',
            ...shorthands.borderColor('var(--primary-neon)'),
        }
    },
    categoryChip: {
        cursor: 'pointer',
        transition: 'all 0.2s',
        ':hover': {
            opacity: 0.8
        }
    },
    formField: {
        display: 'flex',
        flexDirection: 'column',
        gap: '5px',
        marginBottom: '15px'
    }
});

interface KBArticle {
    id: string;
    title: string;
    content: string;
    category: string;
    tags: string[];
}

export const KnowledgeBase: React.FC = () => {
    const styles = useStyles();
    const { instance, accounts } = useMsal();
    const [query, setQuery] = useState('');
    const [articles, setArticles] = useState<KBArticle[]>([]);
    const [loading, setLoading] = useState(false);
    const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
    const userAccount = accounts[0];
    const { t } = useSettings();

    const categories = ['All', 'IT Support', 'HR', 'Finance', 'Facilities', 'Legal'];

    const [selectedArticle, setSelectedArticle] = useState<KBArticle | null>(null);
    const [isEditorOpen, setIsEditorOpen] = useState(false);
    const [editingArticle, setEditingArticle] = useState<Partial<KBArticle>>({});
    const [isSaving, setIsSaving] = useState(false);

    const titleId = useId('title');
    const contentId = useId('content');
    const categoryId = useId('category');

    const getAccessToken = async () => {
        try {
            if (userAccount) {
                const tokenResponse = await instance.acquireTokenSilent({
                    ...loginRequest,
                    account: userAccount
                });
                return tokenResponse.accessToken;
            }
        } catch (error) {
            console.warn("Token acquisition failed", error);
        }
        return "dummy-dev-token";
    };

    const fetchArticles = async () => {
        setLoading(true);
        try {
            const accessToken = await getAccessToken();
            const response = await axios.get('/api/v1/knowledge/articles', {
                headers: { 'Authorization': `Bearer ${accessToken}` }
            });
            setArticles(response.data);
        } catch (error) {
            console.error('Error fetching articles:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = async (searchQuery: string = query, category: string | null = selectedCategory) => {
        setLoading(true);
        try {
            const accessToken = await getAccessToken();
            const params: any = {};
            if (searchQuery) params.query = searchQuery;
            if (category && category !== 'All') params.category = category;

            const endpoint = searchQuery ? '/api/v1/knowledge/search' : '/api/v1/knowledge/articles';

            const response = await axios.get(endpoint, {
                params,
                headers: { 'Authorization': `Bearer ${accessToken}` }
            });

            // Search returns { results: [] }, List returns []
            const data = searchQuery ? response.data.results : response.data;

            // Client-side filter for category if using list endpoint
            let filtered = data;
            if (!searchQuery && category && category !== 'All') {
                filtered = data.filter((a: KBArticle) => a.category === category || (category === 'IT Support' && a.category === 'it_support'));
            }

            setArticles(filtered);
        } catch (error) {
            console.error('Error searching KB:', error);
        } finally {
            setLoading(false);
        }
    };

    // Initial load
    useEffect(() => {
        fetchArticles();
    }, []);

    const onCategoryClick = (cat: string) => {
        setSelectedCategory(cat);
        handleSearch(query, cat);
    };

    const handleSave = async () => {
        if (!editingArticle.title || !editingArticle.content || !editingArticle.category) return;

        setIsSaving(true);
        try {
            const accessToken = await getAccessToken();
            const mapCategoryToEnum = (cat: string) => {
                switch (cat) {
                    case 'IT Support': return 'it_support';
                    case 'HR': return 'hr_inquiry';
                    case 'Facilities': return 'facilities';
                    case 'Legal': return 'legal';
                    case 'Finance': return 'finance';
                    default: return 'unknown';
                }
            };

            const payload = {
                title: editingArticle.title,
                content: editingArticle.content,
                category: mapCategoryToEnum(editingArticle.category),
                tags: editingArticle.tags || [],
                source: 'Manual'
            };

            if (editingArticle.id) {
                // Update
                await axios.put(`/api/v1/knowledge/articles/${editingArticle.id}`, payload, {
                    headers: { 'Authorization': `Bearer ${accessToken}` }
                });
            } else {
                // Create
                await axios.post('/api/v1/knowledge/articles', payload, {
                    headers: { 'Authorization': `Bearer ${accessToken}` }
                });
            }
            setIsEditorOpen(false);
            setEditingArticle({});
            fetchArticles();
        } catch (error) {
            console.error('Error saving article:', error);
            alert('Failed to save article');
        } finally {
            setIsSaving(false);
        }
    };

    const handleDelete = async (id: string, e: React.MouseEvent) => {
        e.stopPropagation();
        if (!window.confirm(t('Are you sure you want to delete this article?'))) return;

        try {
            const accessToken = await getAccessToken();
            await axios.delete(`/api/v1/knowledge/articles/${id}`, {
                headers: { 'Authorization': `Bearer ${accessToken}` }
            });
            fetchArticles();
            if (selectedArticle?.id === id) setSelectedArticle(null);
        } catch (error) {
            console.error('Error deleting article:', error);
        }
    };

    const openEditor = (article?: KBArticle, e?: React.MouseEvent) => {
        if (e) e.stopPropagation();
        setEditingArticle(article || { category: 'IT Support' });
        setIsEditorOpen(true);
    };

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <div>
                    <Text size={600} weight="bold" block>{t('Knowledge Base')}</Text>
                    <Text style={{ color: 'var(--text-secondary)' }}>
                        {t('Manage and search solution articles.')}
                    </Text>
                </div>
                <Button
                    appearance="primary"
                    icon={<Add24Regular />}
                    onClick={() => openEditor()}
                >
                    {t('New Article')}
                </Button>
            </div>

            <div className={styles.searchContainer}>
                <Search24Regular style={{ color: 'var(--primary-neon)' }} />
                <Input
                    placeholder={t('Search knowledge base...')}
                    value={query}
                    onChange={(_e, data) => setQuery(data.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                    style={{ flex: 1, border: 'none', background: 'transparent' }}
                />
                <Button appearance="subtle" onClick={() => handleSearch()}>{t('Search')}</Button>
            </div>

            {/* Categories */}
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                {categories.map(cat => (
                    <Badge
                        key={cat}
                        className={styles.categoryChip}
                        onClick={() => onCategoryClick(cat)}
                        shape="rounded"
                        style={{
                            backgroundColor: selectedCategory === cat || (cat === 'All' && !selectedCategory) ? 'var(--primary-neon)' : 'transparent',
                            border: selectedCategory === cat || (cat === 'All' && !selectedCategory) ? 'none' : '1px solid var(--glass-border)',
                            color: selectedCategory === cat || (cat === 'All' && !selectedCategory) ? 'var(--bg-dark)' : 'var(--text-primary)',
                            cursor: 'pointer'
                        }}
                    >
                        {cat}
                    </Badge>
                ))}
            </div>

            {loading ? (
                <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
                    <Spinner label={t('Loading articles...')} />
                </div>
            ) : (
                <div className={styles.resultsGrid}>
                    {articles.map((article) => (
                        <Card key={article.id} className={styles.articleCard} onClick={() => setSelectedArticle(article)}>
                            <CardHeader
                                header={
                                    <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
                                        <Text weight="bold">{article.title}</Text>
                                        <div style={{ display: 'flex', gap: '5px' }}>
                                            <Button
                                                icon={<Edit24Regular />}
                                                appearance="transparent"
                                                size="small"
                                                onClick={(e) => openEditor(article, e)}
                                            />
                                            <Button
                                                icon={<Delete24Regular />}
                                                appearance="transparent"
                                                size="small"
                                                style={{ color: 'var(--status-error)' }}
                                                onClick={(e) => handleDelete(article.id, e)}
                                            />
                                        </div>
                                    </div>
                                }
                                description={<Text size={200} style={{ color: 'var(--text-muted)' }}>{article.category}</Text>}
                            />
                            <div style={{ padding: '0 12px 12px 12px' }}>
                                <Text className="text-clamp-3" style={{ color: 'var(--text-secondary)' }}>
                                    {article.content.substring(0, 150)}...
                                </Text>
                            </div>
                        </Card>
                    ))}
                    {articles.length === 0 && !loading && (
                        <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                            <BookOpen24Regular style={{ fontSize: '48px', marginBottom: '10px', opacity: 0.5 }} />
                            <Text block>{t('No articles found.')}</Text>
                        </div>
                    )}
                </div>
            )}

            {/* Article Detail Dialog */}
            {selectedArticle && !isEditorOpen && (
                <Dialog open={!!selectedArticle} onOpenChange={() => setSelectedArticle(null)}>
                    <DialogSurface style={{ maxWidth: '800px', width: '90%' }}>
                        <DialogBody>
                            <DialogTitle
                                action={
                                    <Button appearance="subtle" aria-label="close" onClick={() => setSelectedArticle(null)}>Close</Button>
                                }
                            >
                                {selectedArticle.title}
                            </DialogTitle>
                            <DialogContent>
                                <Badge appearance="filled" color="brand" style={{ marginBottom: '20px' }}>{selectedArticle.category}</Badge>
                                <div style={{ lineHeight: '1.6', color: 'var(--text-primary)', whiteSpace: 'pre-wrap' }}>
                                    {selectedArticle.content}
                                </div>
                            </DialogContent>
                        </DialogBody>
                    </DialogSurface>
                </Dialog>
            )}

            {/* Editor Dialog */}
            <Dialog open={isEditorOpen} onOpenChange={() => setIsEditorOpen(false)}>
                <DialogSurface style={{ maxWidth: '600px', width: '90%' }}>
                    <DialogBody>
                        <DialogTitle>{editingArticle.id ? t('Edit Article') : t('New Article')}</DialogTitle>
                        <DialogContent>
                            <div className={styles.formField}>
                                <Label htmlFor={titleId}>{t('Title')}</Label>
                                <Input
                                    id={titleId}
                                    value={editingArticle.title || ''}
                                    onChange={(_e, d) => setEditingArticle({ ...editingArticle, title: d.value })}
                                />
                            </div>
                            <div className={styles.formField}>
                                <Label htmlFor={categoryId}>{t('Category')}</Label>
                                <Dropdown
                                    id={categoryId}
                                    value={editingArticle.category || ''}
                                    selectedOptions={editingArticle.category ? [editingArticle.category] : []}
                                    onOptionSelect={(_e, d) => setEditingArticle({ ...editingArticle, category: d.optionValue as string })}
                                >
                                    {categories.filter(c => c !== 'All').map(c => (
                                        <Option key={c} value={c}>{c}</Option>
                                    ))}
                                </Dropdown>
                            </div>
                            <div className={styles.formField}>
                                <Label htmlFor={contentId}>{t('Content')}</Label>
                                <Textarea
                                    id={contentId}
                                    value={editingArticle.content || ''}
                                    onChange={(_e, d) => setEditingArticle({ ...editingArticle, content: d.value })}
                                    rows={10}
                                />
                            </div>
                        </DialogContent>
                        <DialogActions>
                            <Button appearance="secondary" onClick={() => setIsEditorOpen(false)}>{t('Cancel')}</Button>
                            <Button appearance="primary" onClick={handleSave} disabled={isSaving}>
                                {isSaving ? t('Saving...') : t('Save')}
                            </Button>
                        </DialogActions>
                    </DialogBody>
                </DialogSurface>
            </Dialog>
        </div>
    );
};
