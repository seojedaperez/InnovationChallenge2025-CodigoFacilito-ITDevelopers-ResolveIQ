import React from 'react';
import {
    Text,
    makeStyles,
    shorthands,
    Switch,
    Dropdown,
    Option,
    Avatar,
    Divider,
    Badge
} from '@fluentui/react-components';
import {
    DarkTheme24Regular,
    Alert24Regular,
    Person24Regular,
    Info24Regular
} from '@fluentui/react-icons';
import { useSettings } from '../context/SettingsContext';
import { useMsal } from "@azure/msal-react";

const useStyles = makeStyles({
    container: {
        display: 'flex',
        flexDirection: 'column',
        gap: '20px',
        height: '100%',
        maxWidth: '800px',
        margin: '0 auto',
        width: '100%',
        ...shorthands.padding('20px'),
        overflowY: 'auto'
    },
    section: {
        backgroundColor: 'var(--bg-card)',
        borderRadius: '16px',
        ...shorthands.padding('24px'),
        border: 'var(--glass-border)',
        display: 'flex',
        flexDirection: 'column',
        gap: '20px'
    },
    sectionHeader: {
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        marginBottom: '10px'
    },
    settingRow: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '12px 0',
        '@media (max-width: 600px)': {
            flexDirection: 'column',
            alignItems: 'flex-start',
            gap: '10px'
        }
    },
    settingInfo: {
        display: 'flex',
        flexDirection: 'column',
        gap: '4px'
    }
});

export const Settings: React.FC = () => {
    const styles = useStyles();
    const { theme, toggleTheme, language, setLanguage, notifications, toggleNotification, accessibility, setColorBlindMode, setWcagLevel, t } = useSettings();
    const { accounts } = useMsal();
    const userAccount = accounts[0];

    return (
        <div className={styles.container}>
            <Text size={600} weight="bold" style={{ marginBottom: '10px' }}>{t('Settings')}</Text>
            <Text style={{ color: 'var(--text-secondary)', marginBottom: '20px' }}>
                {t('Manage your preferences and account settings.')}
            </Text>

            {/* Profile Section */}
            <div className={styles.section}>
                <div className={styles.sectionHeader}>
                    <Person24Regular style={{ color: 'var(--primary-neon)' }} />
                    <Text size={400} weight="semibold">{t('Profile')}</Text>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                    <Avatar
                        name={userAccount?.name || 'User'}
                        size={64}
                        color="brand"
                    />
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                        <Text size={400} weight="semibold">{userAccount?.name || t('Guest User')}</Text>
                        <Text style={{ color: 'var(--text-muted)' }}>{userAccount?.username || 'user@example.com'}</Text>
                        <Badge appearance="tint" color="brand">{t('Employee')}</Badge>
                    </div>
                </div>
            </div>

            {/* Appearance & Language */}
            <div className={styles.section}>
                <div className={styles.sectionHeader}>
                    <DarkTheme24Regular style={{ color: '#FFBB28' }} />
                    <Text size={400} weight="semibold">{t('Appearance & Language')}</Text>
                </div>

                <div className={styles.settingRow}>
                    <div className={styles.settingInfo}>
                        <Text weight="medium">{t('Dark Mode')}</Text>
                        <Text size={200} style={{ color: 'var(--text-muted)' }}>{t('Use dark theme for the application')}</Text>
                    </div>
                    <Switch checked={theme === 'dark'} onChange={toggleTheme} />
                </div>

                <Divider />

                <div className={styles.settingRow}>
                    <div className={styles.settingInfo}>
                        <Text weight="medium">{t('Language')}</Text>
                        <Text size={200} style={{ color: 'var(--text-muted)' }}>{t('Select your preferred language')}</Text>
                    </div>
                    <Dropdown
                        value={language}
                        selectedOptions={[language]}
                        onOptionSelect={(_, data) => setLanguage(data.optionValue as string)}
                        style={{ minWidth: '150px' }}
                    >
                        <Option value="English" text="English">English</Option>
                        <Option value="Spanish" text="Spanish">Spanish</Option>
                    </Dropdown>
                </div>
            </div>

            {/* Accessibility */}
            <div className={styles.section}>
                <div className={styles.sectionHeader}>
                    <Person24Regular style={{ color: '#b026ff' }} />
                    <Text size={400} weight="semibold">{t('Accessibility')}</Text>
                </div>

                <div className={styles.settingRow}>
                    <div className={styles.settingInfo}>
                        <Text weight="medium">{t('Color Blind Mode')}</Text>
                        <Text size={200} style={{ color: 'var(--text-muted)' }}>{t('Select color profile')}</Text>
                    </div>
                    <Dropdown
                        value={t(accessibility.colorBlindMode === 'normal' ? 'Normal Vision' :
                            accessibility.colorBlindMode === 'protanopia' ? 'Protanopia' :
                                accessibility.colorBlindMode === 'deuteranopia' ? 'Deuteranopia' :
                                    accessibility.colorBlindMode === 'tritanopia' ? 'Tritanopia' : 'High Contrast')}
                        selectedOptions={[accessibility.colorBlindMode]}
                        onOptionSelect={(_, data) => setColorBlindMode(data.optionValue as any)}
                        style={{ minWidth: '200px' }}
                    >
                        <Option value="normal" text={t('Normal Vision')}>{t('Normal Vision')}</Option>
                        <Option value="protanopia" text={t('Protanopia')}>{t('Protanopia')}</Option>
                        <Option value="deuteranopia" text={t('Deuteranopia')}>{t('Deuteranopia')}</Option>
                        <Option value="tritanopia" text={t('Tritanopia')}>{t('Tritanopia')}</Option>
                        <Option value="high-contrast" text={t('High Contrast')}>{t('High Contrast')}</Option>
                    </Dropdown>
                </div>

                <Divider />

                <div className={styles.settingRow}>
                    <div className={styles.settingInfo}>
                        <Text weight="medium">{t('WCAG Level')}</Text>
                        <Text size={200} style={{ color: 'var(--text-muted)' }}>{t('Contrast and readability standards')}</Text>
                    </div>
                    <Dropdown
                        value={accessibility.wcagLevel}
                        selectedOptions={[accessibility.wcagLevel]}
                        onOptionSelect={(_, data) => setWcagLevel(data.optionValue as any)}
                        style={{ minWidth: '100px' }}
                    >
                        <Option value="A" text="A">A (Normal Text)</Option>
                        <Option value="AA" text="AA">AA (Large Text)</Option>
                        <Option value="AAA" text="AAA">AAA (Extra Large Text)</Option>
                    </Dropdown>
                </div>
            </div>

            {/* Notifications */}
            <div className={styles.section}>
                <div className={styles.sectionHeader}>
                    <Alert24Regular style={{ color: '#FF8042' }} />
                    <Text size={400} weight="semibold">{t('Notifications')}</Text>
                </div>

                <div className={styles.settingRow}>
                    <div className={styles.settingInfo}>
                        <Text weight="medium">{t('Email Notifications')}</Text>
                        <Text size={200} style={{ color: 'var(--text-muted)' }}>{t('Receive updates via email')}</Text>
                    </div>
                    <Switch checked={notifications.email} onChange={() => toggleNotification('email')} />
                </div>

                <div className={styles.settingRow}>
                    <div className={styles.settingInfo}>
                        <Text weight="medium">{t('Browser Notifications')}</Text>
                        <Text size={200} style={{ color: 'var(--text-muted)' }}>{t('Get push notifications in browser')}</Text>
                    </div>
                    <Switch checked={notifications.browser} onChange={() => toggleNotification('browser')} />
                </div>
            </div>

            {/* About */}
            <div className={styles.section}>
                <div className={styles.sectionHeader}>
                    <Info24Regular style={{ color: '#00C49F' }} />
                    <Text size={400} weight="semibold">{t('About')}</Text>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Text>{t('Version')}</Text>
                    <Text style={{ color: 'var(--text-muted)' }}>1.0.0 (Beta)</Text>
                </div>
            </div>
        </div>
    );
};
