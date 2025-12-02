import React, { useState, useEffect } from 'react';
import {
    Text,
    makeStyles,
    shorthands,
    Table,
    TableHeader,
    TableRow,
    TableHeaderCell,
    TableBody,
    TableCell,
    Badge,
    Spinner
} from '@fluentui/react-components';
import axios from 'axios';
import { useMsal } from "@azure/msal-react";
import { loginRequest } from '../authConfig';
import { Ticket } from '../types';
import { useSettings } from '../context/SettingsContext';

const useStyles = makeStyles({
    container: {
        display: 'flex',
        flexDirection: 'column',
        gap: '20px',
        height: '100%',
        ...shorthands.padding('20px'),
    },
    header: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    tableContainer: {
        overflowY: 'auto',
        backgroundColor: 'var(--bg-card)',
        borderRadius: '12px',
        ...shorthands.padding('10px'),
        flex: 1,
        minHeight: 0,
    },
    desktopView: {
        display: 'flex',
        flexDirection: 'column',
        flex: 1,
        minHeight: 0,
        '@media (max-width: 768px)': {
            display: 'none',
        }
    },
    mobileView: {
        display: 'none',
        flexDirection: 'column',
        gap: '15px',
        overflowY: 'auto',
        '@media (max-width: 768px)': {
            display: 'flex',
        }
    }
});

export const MyTickets: React.FC = () => {
    const styles = useStyles();
    const { instance, accounts } = useMsal();
    const [tickets, setTickets] = useState<Ticket[]>([]);
    const [loading, setLoading] = useState(true);
    const userAccount = accounts[0];
    const { t } = useSettings();

    useEffect(() => {
        const fetchTickets = async () => {
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

                const response = await axios.get('/api/v1/tickets', {
                    headers: { 'Authorization': `Bearer ${accessToken}` }
                });
                const sortedTickets = response.data.sort((a: Ticket, b: Ticket) =>
                    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
                );
                setTickets(sortedTickets);
            } catch (error) {
                console.error('Error fetching tickets:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchTickets();
    }, [instance, userAccount]);

    const getStatusColor = (status: string) => {
        switch (status.toLowerCase()) {
            case 'open': return 'success';
            case 'in_progress': return 'warning';
            case 'resolved': return 'brand';
            default: return 'neutral';
        }
    };

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <Text size={600} weight="bold">{t('My Tickets')}</Text>
            </div>

            {loading ? (
                <Spinner label={t('Loading tickets...')} />
            ) : (
                <>
                    {/* Desktop Table View */}
                    <div className={styles.desktopView}>
                        <div className={styles.tableContainer}>
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHeaderCell>{t('Ticket ID')}</TableHeaderCell>
                                        <TableHeaderCell>{t('Description')}</TableHeaderCell>
                                        <TableHeaderCell>{t('Category')}</TableHeaderCell>
                                        <TableHeaderCell>{t('Date')}</TableHeaderCell>
                                        <TableHeaderCell>{t('IP')}</TableHeaderCell>
                                        <TableHeaderCell>{t('Country')}</TableHeaderCell>
                                        <TableHeaderCell>{t('Status')}</TableHeaderCell>
                                        <TableHeaderCell>{t('Priority')}</TableHeaderCell>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {tickets.map((ticket) => (
                                        <TableRow key={ticket.id}>
                                            <TableCell>{ticket.id}</TableCell>
                                            <TableCell>{ticket.description.substring(0, 50)}...</TableCell>
                                            <TableCell>{ticket.category}</TableCell>
                                            <TableCell>{new Date(ticket.created_at).toLocaleString()}</TableCell>
                                            <TableCell style={{ maxWidth: '150px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={ticket.ip_address}>
                                                {ticket.ip_address || '-'}
                                            </TableCell>
                                            <TableCell>{ticket.country || '-'}</TableCell>
                                            <TableCell>
                                                <Badge appearance="filled" color={getStatusColor(ticket.status) as any}>
                                                    {ticket.status}
                                                </Badge>
                                            </TableCell>
                                            <TableCell>{ticket.priority}</TableCell>
                                        </TableRow>
                                    ))}
                                    {tickets.length === 0 && (
                                        <TableRow>
                                            <TableCell colSpan={5} style={{ textAlign: 'center', padding: '20px' }}>
                                                {t('No tickets found.')}
                                            </TableCell>
                                        </TableRow>
                                    )}
                                </TableBody>
                            </Table>
                        </div>
                    </div>

                    {/* Mobile Card View */}
                    <div className={styles.mobileView}>
                        {tickets.map((ticket) => (
                            <div key={ticket.id} className="glass-panel" style={{ padding: '15px', borderRadius: '12px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <Text weight="bold">#{ticket.id}</Text>
                                    <Badge appearance="filled" color={getStatusColor(ticket.status) as any}>
                                        {ticket.status}
                                    </Badge>
                                </div>
                                <Text>{ticket.description}</Text>
                                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: 'var(--text-muted)' }}>
                                    <span>{ticket.category}</span>
                                    <span>{new Date(ticket.created_at).toLocaleString()}</span>
                                    <span>{ticket.priority}</span>
                                </div>
                                <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                                    {ticket.ip_address && <span>IP: {ticket.ip_address} </span>}
                                    {ticket.country && <span>({ticket.country})</span>}
                                </div>
                            </div>
                        ))}
                        {tickets.length === 0 && (
                            <div style={{ textAlign: 'center', padding: '20px', color: 'var(--text-muted)' }}>
                                {t('No tickets found.')}
                            </div>
                        )}
                    </div>
                </>
            )}
        </div>
    );
};
