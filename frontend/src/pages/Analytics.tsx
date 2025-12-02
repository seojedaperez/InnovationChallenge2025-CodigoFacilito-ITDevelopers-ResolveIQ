import React, { useState, useEffect } from 'react';
import {
    Text,
    makeStyles,
    shorthands,
    Spinner
} from '@fluentui/react-components';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    LineChart,
    Line
} from 'recharts';
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
        width: '100%',
        flex: 1,
        ...shorthands.padding('20px'),
        overflowY: 'auto'
    },
    header: {
        marginBottom: '20px',
    },
    statsGrid: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '20px',
        marginBottom: '30px',
    },
    statCard: {
        backgroundColor: 'var(--bg-card)',
        borderRadius: '12px',
        ...shorthands.padding('20px'),
        display: 'flex',
        flexDirection: 'column',
        gap: '10px',
        border: 'var(--glass-border)',
    },
    chartsGrid: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
        gap: '20px',
        '@media (max-width: 768px)': {
            gridTemplateColumns: '1fr',
        }
    },
    chartCard: {
        backgroundColor: 'var(--bg-card)',
        borderRadius: '16px',
        ...shorthands.padding('20px'),
        height: '400px',
        border: 'var(--glass-border)',
        display: 'flex',
        flexDirection: 'column',
        '@media (max-width: 768px)': {
            height: '300px',
        }
    }
});

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

export const Analytics: React.FC = () => {
    const styles = useStyles();
    const { instance, accounts } = useMsal();
    const [metrics, setMetrics] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const userAccount = accounts[0];
    const { t } = useSettings();

    useEffect(() => {
        const fetchMetrics = async () => {
            try {
                let accessToken = "";
                try {
                    if (userAccount) {
                        const tokenResponse = await instance.acquireTokenSilent({
                            ...loginRequest,
                            account: userAccount
                        });
                        accessToken = tokenResponse.accessToken;
                    }
                } catch (error) {
                    console.warn("Token acquisition failed", error);
                    accessToken = "dummy-dev-token";
                }
                if (!accessToken) accessToken = "dummy-dev-token";

                const response = await axios.get('/api/v1/metrics', {
                    headers: { 'Authorization': `Bearer ${accessToken}` }
                });
                setMetrics(response.data);
            } catch (error) {
                console.error('Error fetching metrics:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchMetrics();
    }, [instance, userAccount]);

    if (loading) {
        return (
            <div className={styles.container} style={{ alignItems: 'center', justifyContent: 'center' }}>
                <Spinner label={t('Loading analytics...')} />
            </div>
        );
    }

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <Text size={600} weight="bold">{t('Analytics')}</Text>
                <Text block style={{ color: 'var(--text-secondary)', marginTop: '5px' }}>
                    {t('Real-time insights into service desk performance.')}
                </Text>
            </div>

            {/* Key Metrics */}
            <div className={styles.statsGrid}>
                <div className={styles.statCard}>
                    <Text size={200} style={{ color: 'var(--text-muted)', textTransform: 'uppercase' }}>{t('Total Tickets')}</Text>
                    <Text size={800} weight="bold" style={{ color: 'var(--primary-neon)' }}>{metrics?.total_tickets || 0}</Text>
                </div>
                <div className={styles.statCard}>
                    <Text size={200} style={{ color: 'var(--text-muted)', textTransform: 'uppercase' }}>{t('Avg Resolution Time')}</Text>
                    <Text size={800} weight="bold" style={{ color: '#00C49F' }}>{metrics?.average_resolution_time_hours?.toFixed(1) || 0}h</Text>
                </div>
                <div className={styles.statCard}>
                    <Text size={200} style={{ color: 'var(--text-muted)', textTransform: 'uppercase' }}>{t('CSAT Score')}</Text>
                    <Text size={800} weight="bold" style={{ color: '#FFBB28' }}>{metrics?.customer_satisfaction_score?.toFixed(1) || 0}/5</Text>
                </div>
                <div className={styles.statCard}>
                    <Text size={200} style={{ color: 'var(--text-muted)', textTransform: 'uppercase' }}>{t('AI Confidence')}</Text>
                    <Text size={800} weight="bold" style={{ color: '#8884d8' }}>98%</Text>
                </div>
            </div>

            {/* Charts */}
            <div className={styles.chartsGrid}>
                <div className={styles.chartCard}>
                    <Text weight="semibold" style={{ marginBottom: '20px' }}>{t('Tickets by Category')}</Text>
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={Object.entries(metrics?.tickets_by_category || {}).map(([name, value]) => ({ name, value }))}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                            <XAxis dataKey="name" stroke="var(--text-muted)" />
                            <YAxis stroke="var(--text-muted)" />
                            <Tooltip
                                contentStyle={{ backgroundColor: 'var(--bg-card)', border: 'var(--glass-border)', color: 'var(--text-primary)' }}
                            />
                            <Bar dataKey="value" fill="var(--primary-neon)" />
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                <div className={styles.chartCard}>
                    <Text weight="semibold" style={{ marginBottom: '20px' }}>{t('Ticket Status Distribution')}</Text>
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={Object.entries(metrics?.tickets_by_status || {}).map(([name, value]) => ({ name, value }))}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={80}
                                fill="#8884d8"
                                paddingAngle={5}
                                dataKey="value"
                            >
                                {Object.entries(metrics?.tickets_by_status || {}).map((_entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip contentStyle={{ backgroundColor: 'var(--bg-card)', border: 'var(--glass-border)', color: 'var(--text-primary)' }} />
                            <Legend />
                        </PieChart>
                    </ResponsiveContainer>
                </div>

                <div className={styles.chartCard} style={{ gridColumn: '1 / -1' }}>
                    <Text weight="semibold" style={{ marginBottom: '20px' }}>{t('Resolution Time Trend (Last 7 Days)')}</Text>
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={metrics?.resolution_time_trend || []}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                            <XAxis dataKey="date" stroke="var(--text-muted)" />
                            <YAxis stroke="var(--text-muted)" />
                            <Tooltip contentStyle={{ backgroundColor: 'var(--bg-card)', border: 'var(--glass-border)', color: 'var(--text-primary)' }} />
                            <Line type="monotone" dataKey="hours" stroke="#8884d8" strokeWidth={2} />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
};
