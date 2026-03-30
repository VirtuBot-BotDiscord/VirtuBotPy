const API_URL = localStorage.getItem('apiUrl') || `http://${window.location.hostname}:3001`;

async function fetchAPI(endpoint, options = {}) {
    try {

        const token = localStorage.getItem('discord_token');
        

        let url = `${API_URL}${endpoint}`;
        if (token) {
            const separator = endpoint.includes('?') ? '&' : '?';
            url += `${separator}token=${encodeURIComponent(token)}`;
        }
        
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });


        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            console.error('Réponse non-JSON reçue:', await response.text());
            throw new Error('Le serveur a retourné une réponse invalide (HTML au lieu de JSON). Vérifiez que l\'API est démarrée.');
        }

        const data = await response.json();

        if (!response.ok) {

            if (response.status === 401) {
                localStorage.removeItem('discord_token');
                window.location.href = '/login.html';
                throw new Error('Session expirée, veuillez vous reconnecter');
            }
            

            if (response.status === 403) {
                throw new Error(data.message || 'Vous n\'avez pas les permissions pour effectuer cette action');
            }
            
            throw new Error(data.error || `Erreur HTTP ${response.status}`);
        }

        return data;
    } catch (error) {
        console.error('Erreur API:', error);
        

        if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
            throw new Error('Impossible de se connecter à l\'API. Vérifiez que le serveur est démarré sur ' + API_URL);
        }
        
        throw error;
    }
}

async function getBotStats() {
    return fetchAPI('/api/bot/stats');
}

async function getGuilds() {
    return fetchAPI('/api/guilds');
}

async function getGuildDetails(guildId) {
    return fetchAPI(`/api/guilds/${guildId}`);
}

async function getGuildMembers(guildId) {
    return fetchAPI(`/api/guilds/${guildId}/members`);
}

async function getBotCommands() {
    return fetchAPI('/api/bot/commands');
}

async function getCommandLogs() {
    return fetchAPI('/api/logs');
}

async function checkHealth() {
    return fetchAPI('/api/health');
}

async function getGuildBans(guildId) {
    return fetchAPI(`/api/guilds/${guildId}/bans`);
}

async function unbanUser(guildId, userId) {
    return fetchAPI(`/api/guilds/${guildId}/bans/${userId}`, {
        method: 'DELETE'
    });
}

async function getGuildBlacklist(guildId) {
    return fetchAPI(`/api/guilds/${guildId}/blacklist`);
}

async function addUserToBlacklist(guildId, userId, reason) {
    return fetchAPI(`/api/guilds/${guildId}/blacklist/${userId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ reason })
    });
}

async function removeUserFromBlacklist(guildId, userId) {
    return fetchAPI(`/api/guilds/${guildId}/blacklist/${userId}`, {
        method: 'DELETE'
    });
}

async function banUser(guildId, userId, reason) {
    return fetchAPI(`/api/guilds/${guildId}/bans`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: userId, reason })
    });
}
