import React, { createContext, useContext, useState, useEffect } from 'react';

interface SettingsContextType {
    theme: 'dark' | 'light';
    toggleTheme: () => void;
    language: string;
    setLanguage: (lang: string) => void;
    notifications: {
        email: boolean;
        browser: boolean;
    };
    toggleNotification: (type: 'email' | 'browser') => void;
    accessibility: {
        colorBlindMode: 'normal' | 'protanopia' | 'deuteranopia' | 'tritanopia' | 'high-contrast';
        wcagLevel: 'A' | 'AA' | 'AAA';
    };
    setColorBlindMode: (mode: 'normal' | 'protanopia' | 'deuteranopia' | 'tritanopia' | 'high-contrast') => void;
    setWcagLevel: (level: 'A' | 'AA' | 'AAA') => void;
    t: (key: string) => string;
}

const translations: Record<string, Record<string, string>> = {
    'English': {
        'Dashboard': 'Dashboard',
        'My Tickets': 'My Tickets',
        'Knowledge Base': 'Knowledge Base',
        'Analytics': 'Analytics',
        'Settings': 'Settings',
        'Sign Out': 'Sign Out',
        'Autonomous Enterprise Service Mesh': 'Autonomous Enterprise Service Mesh',
        'How can I help you today': 'How can I help you today',
        'Describe your issue...': 'Describe your issue...',
        'Status': 'Status',
        'Category': 'Category',
        'Confidence': 'Confidence',
        'Ticket ID': 'Ticket ID',
        'LIVE REASONING GRAPH': 'LIVE REASONING GRAPH',
        'Active': 'Active',
        'Waiting for input...': 'Waiting for input...',
        'Processing...': 'Processing...',
        'IDLE': 'IDLE',
        'Profile': 'Profile',
        'Appearance & Language': 'Appearance & Language',
        'Dark Mode': 'Dark Mode',
        'Use dark theme for the application': 'Use dark theme for the application',
        'Language': 'Language',
        'Notifications': 'Notifications',
        'Email Notifications': 'Email Notifications',
        'Browser Notifications': 'Browser Notifications',
        'About': 'About',
        'Version': 'Version',
        'Manage your preferences and account settings.': 'Manage your preferences and account settings.',
        'Total Tickets': 'Total Tickets',
        'Avg Resolution Time': 'Avg Resolution Time',
        'CSAT Score': 'CSAT Score',
        'AI Confidence': 'AI Confidence',
        'Tickets by Category': 'Tickets by Category',
        'Ticket Status Distribution': 'Ticket Status Distribution',
        'Resolution Time Trend (Last 7 Days)': 'Resolution Time Trend (Last 7 Days)',
        'Real-time insights into service desk performance.': 'Real-time insights into service desk performance.',
        'Search knowledge base...': 'Search knowledge base...',
        'No articles found.': 'No articles found.',
        'Loading articles...': 'Loading articles...',
        'Loading analytics...': 'Loading analytics...',
        'Loading tickets...': 'Loading tickets...',
        'No tickets found.': 'No tickets found.',
        'Description': 'Description',
        'Priority': 'Priority',
        'Guest User': 'Guest User',
        'User': 'User',
        'Employee': 'Employee',
        'Date': 'Date',
        'IP': 'IP',
        'Country': 'Country',
        'Accessibility': 'Accessibility',
        'Color Blind Mode': 'Color Blind Mode',
        'Select color profile': 'Select color profile',
        'Normal Vision': 'Normal Vision',
        'Protanopia': 'Protanopia (Red weak)',
        'Deuteranopia': 'Deuteranopia (Green weak)',
        'Tritanopia': 'Tritanopia (Blue weak)',
        'High Contrast': 'High Contrast (Monochromatic)',
        'WCAG Level': 'WCAG Level',
        'Contrast and readability standards': 'Text size and readability standards',
        'Text Size': 'Text Size',
        'Adjust text size for better readability': 'Adjust text size for better readability',
        'Normal': 'Normal',
        'Large': 'Large',
        'Extra Large': 'Extra Large'
    },
    'Spanish': {
        'Dashboard': 'Panel Principal',
        'My Tickets': 'Mis Tickets',
        'Knowledge Base': 'Base de Conocimiento',
        'Analytics': 'Analíticas',
        'Settings': 'Configuración',
        'Sign Out': 'Cerrar Sesión',
        'Autonomous Enterprise Service Mesh': 'Malla de Servicios Empresarial Autónoma',
        'How can I help you today': '¿Cómo puedo ayudarte hoy',
        'Describe your issue...': 'Describe tu problema...',
        'Status': 'Estado',
        'Category': 'Categoría',
        'Confidence': 'Confianza',
        'Ticket ID': 'ID del Ticket',
        'LIVE REASONING GRAPH': 'GRÁFICO DE RAZONAMIENTO EN VIVO',
        'Active': 'Activo',
        'Waiting for input...': 'Esperando entrada...',
        'Processing...': 'Procesando...',
        'IDLE': 'INACTIVO',
        'Profile': 'Perfil',
        'Appearance & Language': 'Apariencia e Idioma',
        'Dark Mode': 'Modo Oscuro',
        'Use dark theme for the application': 'Usar tema oscuro para la aplicación',
        'Language': 'Idioma',
        'Notifications': 'Notificaciones',
        'Email Notifications': 'Notificaciones por Correo',
        'Browser Notifications': 'Notificaciones del Navegador',
        'About': 'Acerca de',
        'Version': 'Versión',
        'Manage your preferences and account settings.': 'Gestiona tus preferencias y configuración de cuenta.',
        'Total Tickets': 'Total de Tickets',
        'Avg Resolution Time': 'Tiempo Promedio de Resolución',
        'CSAT Score': 'Puntuación CSAT',
        'AI Confidence': 'Confianza de IA',
        'Tickets by Category': 'Tickets por Categoría',
        'Ticket Status Distribution': 'Distribución de Estado de Tickets',
        'Resolution Time Trend (Last 7 Days)': 'Tendencia de Tiempo de Resolución (Últimos 7 Días)',
        'Real-time insights into service desk performance.': 'Información en tiempo real sobre el rendimiento de la mesa de ayuda.',
        'Search knowledge base...': 'Buscar en la base de conocimiento...',
        'No articles found.': 'No se encontraron artículos.',
        'Loading articles...': 'Cargando artículos...',
        'Loading analytics...': 'Cargando analíticas...',
        'Loading tickets...': 'Cargando tickets...',
        'No tickets found.': 'No se encontraron tickets.',
        'Description': 'Descripción',
        'Priority': 'Prioridad',
        'Guest User': 'Usuario Invitado',
        'User': 'Usuario',
        'Employee': 'Empleado',
        'Date': 'Fecha',
        'IP': 'IP',
        'Country': 'País',
        'Accessibility': 'Accesibilidad',
        'Color Blind Mode': 'Modo Daltonismo',
        'Select color profile': 'Seleccionar perfil de color',
        'Normal Vision': 'Visión Normal',
        'Protanopia': 'Protanopia (Dificultad con rojo)',
        'Deuteranopia': 'Deuteranopia (Dificultad con verde)',
        'Tritanopia': 'Tritanopia (Dificultad con azul)',
        'High Contrast': 'Alto Contraste (Monocromático)',
        'WCAG Level': 'Nivel WCAG',
        'Contrast and readability standards': 'Estándares de tamaño de texto y legibilidad',
        'Text Size': 'Tamaño de Texto',
        'Adjust text size for better readability': 'Ajustar tamaño de texto para mejor lectura',
        'Normal': 'Normal',
        'Large': 'Grande',
        'Extra Large': 'Extra Grande',
        'Related Knowledge Base Articles': 'Artículos Relacionados de la Base de Conocimiento'
    }
};

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

export const SettingsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    // Initialize from localStorage or default
    const [theme, setTheme] = useState<'dark' | 'light'>(() => {
        return (localStorage.getItem('theme') as 'dark' | 'light') || 'dark';
    });

    const [language, setLanguage] = useState(() => {
        return localStorage.getItem('language') || 'English';
    });

    const [notifications, setNotifications] = useState(() => {
        const saved = localStorage.getItem('notifications');
        return saved ? JSON.parse(saved) : { email: true, browser: false };
    });

    const [accessibility, setAccessibility] = useState(() => {
        const saved = localStorage.getItem('accessibility');
        const parsed = saved ? JSON.parse(saved) : {};
        return {
            colorBlindMode: parsed.colorBlindMode || 'normal',
            wcagLevel: parsed.wcagLevel || 'A'
        };
    });

    // Apply theme effect
    useEffect(() => {
        if (theme === 'light') {
            document.body.classList.add('light-mode');
        } else {
            document.body.classList.remove('light-mode');
        }
        localStorage.setItem('theme', theme);
    }, [theme]);

    // Apply accessibility effect
    useEffect(() => {
        // Reset accessibility classes
        document.body.classList.remove(
            'mode-protanopia',
            'mode-deuteranopia',
            'mode-tritanopia',
            'mode-high-contrast',
            'wcag-a',
            'wcag-aa',
            'wcag-aaa',
            'text-normal',
            'text-large',
            'text-xlarge'
        );

        // Apply Color Blind Mode
        if (accessibility.colorBlindMode && accessibility.colorBlindMode !== 'normal') {
            document.body.classList.add(`mode-${accessibility.colorBlindMode}`);
        }

        // Apply WCAG Level (Maps to text size)
        if (accessibility.wcagLevel) {
            document.body.classList.add(`wcag-${accessibility.wcagLevel.toLowerCase()}`);

            // Map WCAG Level to Text Size
            if (accessibility.wcagLevel === 'A') {
                document.body.classList.add('text-normal');
            } else if (accessibility.wcagLevel === 'AA') {
                document.body.classList.add('text-large');
            } else if (accessibility.wcagLevel === 'AAA') {
                document.body.classList.add('text-xlarge');
            }
        }

        localStorage.setItem('accessibility', JSON.stringify(accessibility));
    }, [accessibility]);

    // Persist language
    useEffect(() => {
        localStorage.setItem('language', language);
    }, [language]);

    // Persist notifications
    useEffect(() => {
        localStorage.setItem('notifications', JSON.stringify(notifications));
    }, [notifications]);

    const toggleTheme = () => {
        setTheme(prev => prev === 'dark' ? 'light' : 'dark');
    };

    const toggleNotification = async (type: 'email' | 'browser') => {
        if (type === 'browser' && !notifications.browser) {
            if (!('Notification' in window)) {
                alert('This browser does not support desktop notification');
                return;
            }

            const permission = await Notification.requestPermission();
            if (permission !== 'granted') {
                return;
            }
        }

        setNotifications((prev: any) => ({
            ...prev,
            [type]: !prev[type]
        }));
    };

    const setColorBlindMode = (mode: 'normal' | 'protanopia' | 'deuteranopia' | 'tritanopia' | 'high-contrast') => {
        setAccessibility((prev: any) => ({
            ...prev,
            colorBlindMode: mode
        }));
    };

    const setWcagLevel = (level: 'A' | 'AA' | 'AAA') => {
        setAccessibility((prev: any) => ({
            ...prev,
            wcagLevel: level
        }));
    };

    const t = (key: string) => {
        const lang = translations[language] || translations['English'];
        return lang[key] || key;
    };

    return (
        <SettingsContext.Provider value={{
            theme,
            toggleTheme,
            language,
            setLanguage,
            notifications,
            toggleNotification,
            accessibility,
            setColorBlindMode,
            setWcagLevel,
            t
        }}>
            {children}
        </SettingsContext.Provider>
    );
};

export const useSettings = () => {
    const context = useContext(SettingsContext);
    if (!context) {
        throw new Error('useSettings must be used within a SettingsProvider');
    }
    return context;
};
