import { useMsal } from "@azure/msal-react";
import { loginRequest } from "../authConfig";
import { Button, Text, Title1, makeStyles, shorthands } from '@fluentui/react-components';
import { Person24Regular } from '@fluentui/react-icons';

const useStyles = makeStyles({
    container: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        backgroundColor: 'var(--bg-dark)',
        color: 'white',
        backgroundImage: `
            radial-gradient(circle at 20% 30%, rgba(0, 240, 255, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 70%, rgba(0, 120, 212, 0.1) 0%, transparent 50%)
        `
    },
    card: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '20px',
        ...shorthands.padding('40px'),
        backgroundColor: 'rgba(20, 25, 35, 0.8)',
        backdropFilter: 'blur(10px)',
        borderRadius: '20px',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        boxShadow: '0 0 30px rgba(0, 0, 0, 0.5)',
        maxWidth: '400px',
        width: '100%',
    },
    logo: {
        width: '60px',
        height: '60px',
        borderRadius: '12px',
        background: 'linear-gradient(135deg, #00f0ff 0%, #0078d4 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: '10px',
        boxShadow: '0 0 20px rgba(0, 240, 255, 0.4)',
    },
    button: {
        width: '100%',
        height: '48px',
        fontSize: '16px',
        fontWeight: '600',
        backgroundColor: '#0078d4',
        color: 'white',
        border: 'none',
        ':hover': {
            backgroundColor: '#006cbd',
        }
    }
});

export const Login = () => {
    const { instance } = useMsal();
    const styles = useStyles();

    const handleLogin = () => {
        instance.loginRedirect(loginRequest).catch(e => {
            console.error(e);
        });
    };

    return (
        <div className={styles.container}>
            <div className={styles.card}>
                <div className={styles.logo}>
                    <Person24Regular style={{ fontSize: '32px', color: 'white' }} />
                </div>

                <div style={{ textAlign: 'center' }}>
                    <Title1 style={{ color: 'white', marginBottom: '8px', display: 'block' }}>ResolveIQ</Title1>
                    <Text style={{ color: 'rgba(255,255,255,0.6)' }}>
                        Autonomous Enterprise Service Mesh
                    </Text>
                </div>

                <div style={{ width: '100%', height: '1px', background: 'rgba(255,255,255,0.1)', margin: '10px 0' }} />

                <Button
                    appearance="primary"
                    className={styles.button}
                    onClick={handleLogin}
                    icon={<div style={{ marginRight: '8px' }}>🪟</div>} // Simple Microsoft-ish icon
                >
                    Sign in with Microsoft
                </Button>
            </div>
        </div>
    );
};
