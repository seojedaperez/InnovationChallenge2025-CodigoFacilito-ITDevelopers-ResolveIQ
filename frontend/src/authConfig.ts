import { Configuration, PopupRequest } from "@azure/msal-browser";

// Configurable via environment variables (Vite uses import.meta.env)
// If not set, it will try to use placeholders which will fail, prompting user to config.
export const msalConfig: Configuration = {
    auth: {
        clientId: import.meta.env.VITE_AZURE_AD_CLIENT_ID || "ENTER_CLIENT_ID_HERE",
        authority: `https://login.microsoftonline.com/${import.meta.env.VITE_AZURE_AD_TENANT_ID || "common"}`,
        redirectUri: window.location.origin, // e.g., http://localhost:3000
    },
    cache: {
        cacheLocation: "sessionStorage", // This configures where your cache will be stored
        storeAuthStateInCookie: false, // Set this to "true" if you are having issues on IE11 or Edge
    }
};

// Add scopes here for ID token to be used at Microsoft identity platform endpoints.
export const loginRequest: PopupRequest = {
    scopes: ["User.Read"]
};

// Add the endpoints here for Microsoft Graph API services you'd like to use.
export const graphConfig = {
    graphMeEndpoint: "https://graph.microsoft.com/v1.0/me"
};
