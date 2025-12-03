import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useMemo } from 'react';
import {
  FluentProvider,
  webDarkTheme,
  webLightTheme,
  Theme
} from '@fluentui/react-components';
import { AuthenticatedTemplate, UnauthenticatedTemplate } from "@azure/msal-react";
import { Login } from './components/Login';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { MyTickets } from './pages/MyTickets';
import { KnowledgeBase } from './pages/KnowledgeBase';
import { Analytics } from './pages/Analytics';
import { Settings } from './pages/Settings';
import { useSettings } from './context/SettingsContext';
import './App.css';

// Helper to scale theme fonts
const createScaledTheme = (baseTheme: Theme, scale: number): Theme => {
  if (scale === 1) return baseTheme;

  const scaledTheme = { ...baseTheme };

  const fontTokens = [
    'fontSizeBase100', 'fontSizeBase200', 'fontSizeBase300', 'fontSizeBase400', 'fontSizeBase500', 'fontSizeBase600',
    'fontSizeHero700', 'fontSizeHero800', 'fontSizeHero900', 'fontSizeHero1000'
  ] as const;

  const lineHeightTokens = [
    'lineHeightBase100', 'lineHeightBase200', 'lineHeightBase300', 'lineHeightBase400', 'lineHeightBase500', 'lineHeightBase600',
    'lineHeightHero700', 'lineHeightHero800', 'lineHeightHero900', 'lineHeightHero1000'
  ] as const;

  fontTokens.forEach(token => {
    const value = baseTheme[token];
    if (typeof value === 'string' && value.endsWith('px')) {
      const size = parseInt(value, 10);
      // @ts-ignore - Dynamic key assignment
      scaledTheme[token] = `${Math.round(size * scale)}px`;
    }
  });

  lineHeightTokens.forEach(token => {
    const value = baseTheme[token];
    if (typeof value === 'string' && value.endsWith('px')) {
      const size = parseInt(value, 10);
      // @ts-ignore - Dynamic key assignment
      scaledTheme[token] = `${Math.round(size * scale)}px`;
    }
  });

  return scaledTheme;
};

const App: React.FC = () => {
  const { theme, accessibility } = useSettings();

  const activeTheme = useMemo(() => {
    const base = theme === 'dark' ? webDarkTheme : webLightTheme;
    let scale = 1;

    if (accessibility.wcagLevel === 'AA') {
      scale = 1.2; // 20% larger
    } else if (accessibility.wcagLevel === 'AAA') {
      scale = 1.5; // 50% larger
    }

    return createScaledTheme(base, scale);
  }, [theme, accessibility.wcagLevel]);

  return (
    <FluentProvider theme={activeTheme}>
      <UnauthenticatedTemplate>
        <Login />
      </UnauthenticatedTemplate>

      <AuthenticatedTemplate>
        <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<Dashboard />} />
              <Route path="tickets" element={<MyTickets />} />
              <Route path="kb" element={<KnowledgeBase />} />
              <Route path="analytics" element={<Analytics />} />
              <Route path="settings" element={<Settings />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthenticatedTemplate>
    </FluentProvider>
  );
};

export default App;
