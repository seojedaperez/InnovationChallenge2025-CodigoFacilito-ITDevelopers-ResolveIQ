import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
    Text,
    Button,
    makeStyles,
    shorthands,
    Avatar,
    mergeClasses
} from '@fluentui/react-components';
import { useMsal } from "@azure/msal-react";
import { Navigation24Regular, Dismiss24Regular } from '@fluentui/react-icons';
import { useSettings } from '../context/SettingsContext';

const useStyles = makeStyles({
    appContainer: {
        display: 'flex',
        height: '100vh',
        backgroundColor: 'var(--bg-dark)',
        color: 'var(--text-primary)',
        overflow: 'hidden',
    },
    sidebar: {
        width: '260px',
        backgroundColor: 'var(--bg-card)',
        borderRight: 'var(--glass-border)',
        display: 'flex',
        flexDirection: 'column',
        ...shorthands.padding('20px'),
        zIndex: 100,
        transition: 'transform 0.3s ease-in-out',
        '@media (max-width: 768px)': {
            position: 'fixed',
            top: 0,
            left: 0,
            bottom: 0,
            transform: 'translateX(-100%)',
        }
    },
    sidebarOpen: {
        '@media (max-width: 768px)': {
            transform: 'translateX(0)',
        }
    },
    overlay: {
        display: 'none',
        '@media (max-width: 768px)': {
            display: 'block',
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            zIndex: 90,
        }
    },
    mainContent: {
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        width: '100%' // Ensure it takes full width
    },
    header: {
        height: '70px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        ...shorthands.padding('0', '30px'),
        borderBottom: 'var(--glass-border)',
        backgroundColor: 'var(--bg-card)',
        backdropFilter: 'blur(10px)',
        '@media (max-width: 768px)': {
            padding: '0 15px',
        }
    },
    menuButton: {
        display: 'none',
        marginRight: '10px',
        '@media (max-width: 768px)': {
            display: 'inline-flex',
        }
    },
    workspace: {
        flex: 1,
        display: 'flex',
        ...shorthands.padding('20px'),
        gap: '20px',
        overflow: 'hidden',
        '@media (max-width: 768px)': {
            padding: '10px',
            flexDirection: 'column',
            overflowY: 'auto',
        }
    },
    navItem: {
        padding: '12px',
        borderRadius: '8px',
        cursor: 'pointer',
        marginBottom: '5px',
        ':hover': {
            backgroundColor: 'var(--bg-card-hover)'
        }
    },
    activeNavItem: {
        backgroundColor: 'rgba(0, 240, 255, 0.1)',
        color: 'var(--primary-neon)',
    },
    userInfo: {
        textAlign: 'right',
        display: 'none',
        '@media (min-width: 768px)': {
            display: 'block',
        }
    }
});

export const Layout: React.FC = () => {
    const styles = useStyles();
    const { accounts, instance } = useMsal();
    const navigate = useNavigate();
    const location = useLocation();
    const userAccount = accounts[0];
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const { t } = useSettings();

    const handleLogout = () => {
        instance.logoutPopup().catch(e => {
            console.error(e);
        });
    };

    const handleNavClick = (path: string) => {
        navigate(path);
        setIsMobileMenuOpen(false); // Close menu on mobile after click
    };

    const navItems = [
        { name: t('Dashboard'), path: '/' },
        { name: t('My Tickets'), path: '/tickets' },
        { name: t('Knowledge Base'), path: '/kb' },
        { name: t('Analytics'), path: '/analytics' },
        { name: t('Settings'), path: '/settings' }
    ];

    return (
        <div className={styles.appContainer}>
            {/* Mobile Overlay */}
            {isMobileMenuOpen && (
                <div className={styles.overlay} onClick={() => setIsMobileMenuOpen(false)} />
            )}

            {/* Sidebar */}
            <aside className={mergeClasses(styles.sidebar, isMobileMenuOpen && styles.sidebarOpen, "glass-panel")}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '40px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{ width: '32px', height: '32px', background: 'var(--primary-neon)', borderRadius: '8px' }}></div>
                        <Text size={500} weight="bold" style={{ color: 'var(--text-primary)' }}>ResolveIQ</Text>
                    </div>
                    {/* Close button for mobile */}
                    <div style={{ display: 'none' }} className={styles.menuButton}>
                        <Button
                            appearance="subtle"
                            icon={<Dismiss24Regular />}
                            onClick={() => setIsMobileMenuOpen(false)}
                            style={{ display: isMobileMenuOpen ? 'flex' : 'none' }}
                        />
                    </div>
                </div>

                <nav style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                    {navItems.map((item) => {
                        const isActive = location.pathname === item.path;
                        return (
                            <div
                                key={item.name}
                                className={`${styles.navItem} ${isActive ? styles.activeNavItem : ''}`}
                                onClick={() => handleNavClick(item.path)}
                                style={{
                                    color: isActive ? 'var(--primary-neon)' : 'var(--text-secondary)'
                                }}
                            >
                                <Text>{item.name}</Text>
                            </div>
                        );
                    })}
                    <div style={{ marginTop: 'auto', paddingTop: '20px', borderTop: 'var(--glass-border)' }}>
                        <Button appearance="subtle" onClick={handleLogout} style={{ color: 'var(--text-muted)' }}>{t('Sign Out')}</Button>
                    </div>
                </nav>
            </aside>

            {/* Main Content */}
            <div className={styles.mainContent}>
                <header className={styles.header}>
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                        <Button
                            appearance="subtle"
                            icon={<Navigation24Regular />}
                            className={styles.menuButton}
                            onClick={() => setIsMobileMenuOpen(true)}
                        />
                        <Text size={400} weight="semibold" style={{ color: 'var(--text-secondary)' }}>
                            {t('Autonomous Enterprise Service Mesh')}
                        </Text>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                        <div className={styles.userInfo}>
                            <Text block size={300} weight="semibold">{userAccount?.name || t('User')}</Text>
                            <Text block size={200} style={{ color: 'var(--text-muted)' }}>{userAccount?.username || t('Employee')}</Text>
                        </div>
                        <Avatar name={userAccount?.name || 'User'} color="brand" />
                    </div>
                </header>

                <div className={styles.workspace}>
                    <Outlet />
                </div>
            </div>
        </div>
    );
};
