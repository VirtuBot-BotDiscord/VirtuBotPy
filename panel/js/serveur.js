let currentGuildId = null;
let guildData = null;
let discordUser = null;


function addTokenToUrl(url) {
    const token = localStorage.getItem('discord_token');
    if (!token) return url;
    const separator = url.includes('?') ? '&' : '?';
    return `${url}${separator}token=${encodeURIComponent(token)}`;
}

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Dashboard Serveur chargé');
    
    const token = localStorage.getItem('discord_token');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }
    
    const urlParams = new URLSearchParams(window.location.search);
    currentGuildId = urlParams.get('guild');
    
    if (!currentGuildId) {
        alert('ID du serveur manquant');
        window.location.href = 'index.html';
        return;
    }
    
    try {
        await loadUserData();
    } catch (error) {
        console.error('Erreur auth:', error);
        localStorage.removeItem('discord_token');
        window.location.href = 'login.html';
        return;
    }
    
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    
    menuToggle.addEventListener('click', () => {
        sidebar.classList.toggle('active');
    });

    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            const page = item.getAttribute('data-page');
            if (page) {
                e.preventDefault();
                navigateToPage(page);
                
                navItems.forEach(nav => nav.classList.remove('active'));
                item.classList.add('active');
                
                sidebar.classList.remove('active');
            }
        });
    });

    await loadGuildOverview();
    await checkBotStatus();
    
    setInterval(checkBotStatus, 30000);
});

async function loadUserData() {
    const token = localStorage.getItem('discord_token');
    
    const response = await fetch('https://discord.com/api/users/@me', {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!response.ok) throw new Error('Auth failed');
    discordUser = await response.json();
    localStorage.setItem('discord_user', JSON.stringify(discordUser));
    
    const userAvatar = document.getElementById('userAvatar');
    const userName = document.getElementById('userName');
    
    if (discordUser) {
        userName.textContent = discordUser.username;
        if (discordUser.avatar) {
            const isAnimated = discordUser.avatar.startsWith('a_');
            const extension = isAnimated ? 'gif' : 'png';
            const avatarUrl = `https://cdn.discordapp.com/avatars/${discordUser.id}/${discordUser.avatar}.${extension}?size=128`;
            userAvatar.src = avatarUrl;
            userAvatar.style.display = 'block';
            userAvatar.style.cursor = 'pointer';
            
            userAvatar.onclick = () => showUserProfile();
        }
    }
}

function logout() {
    localStorage.removeItem('discord_token');
    localStorage.removeItem('discord_user');
    window.location.href = 'login.html';
}

function navigateToPage(pageName) {
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => page.classList.remove('active'));
    
    const targetPage = document.getElementById(`${pageName}-page`);
    if (targetPage) {
        targetPage.classList.add('active');
        
        switch(pageName) {
            case 'overview':
                loadGuildOverview();
                break;
            case 'logs':
                loadGuildLogs();
                break;
            case 'bans':
                loadGuildBans();
                break;
            case 'members':
                loadGuildMembers();
                break;
            case 'blacklist':
                loadGuildBlacklist();
                break;
            case 'warns':
                loadWarnsPage();
                break;
            case 'settings':
                loadGuildSettings();
                break;
            case 'tickets':
                loadTicketsPage();
                break;
        }
    }
}

async function checkBotStatus() {
    try {
        const health = await checkHealth();
        const botStatus = document.getElementById('botStatus');
        
        if (health.bot_ready) {
            botStatus.innerHTML = '<i class="fas fa-circle"></i> En ligne';
            botStatus.classList.add('online');
            botStatus.classList.remove('offline');
        } else {
            botStatus.innerHTML = '<i class="fas fa-circle"></i> Hors ligne';
            botStatus.classList.add('offline');
            botStatus.classList.remove('online');
        }
    } catch (error) {
        const botStatus = document.getElementById('botStatus');
        botStatus.innerHTML = '<i class="fas fa-circle"></i> Erreur';
        botStatus.classList.add('offline');
        botStatus.classList.remove('online');
    }
}

async function loadGuildOverview() {
    try {
        guildData = await getGuildDetails(currentGuildId);
        
        const guildName = document.getElementById('guildName');
        const guildIcon = document.getElementById('guildIcon');
        
        guildName.textContent = guildData.name;
        if (guildData.icon) {
            guildIcon.src = guildData.icon;
            guildIcon.style.display = 'block';
        }
        
        const sevenDaysAgo = new Date();
        sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
        
        let newMembersCount = 0;
        if (guildData.members) {
            newMembersCount = guildData.members.filter(m => {
                if (!m.joinedAt) return false;
                return new Date(m.joinedAt) >= sevenDaysAgo;
            }).length;
        }
        
        let newChannelsCount = 0;
        if (guildData.channels) {
            newChannelsCount = guildData.channels.filter(c => {
                if (!c.createdAt) return false;
                return new Date(c.createdAt) >= sevenDaysAgo;
            }).length;
        }
        
        let newRolesCount = 0;
        if (guildData.roles) {
            newRolesCount = guildData.roles.filter(r => {
                if (!r.createdAt) return false;
                return new Date(r.createdAt) >= sevenDaysAgo;
            }).length;
        }
        
        document.getElementById('memberCount').innerHTML = `${guildData.memberCount || '-'}${newMembersCount > 0 ? ` <span style="color: #10b981; font-size: 0.9rem;">+${newMembersCount}</span>` : ''}`;
        document.getElementById('channelCount').innerHTML = `${guildData.channels?.length || '-'}${newChannelsCount > 0 ? ` <span style="color: #10b981; font-size: 0.9rem;">+${newChannelsCount}</span>` : ''}`;
        document.getElementById('roleCount').innerHTML = `${guildData.roles?.length || '-'}${newRolesCount > 0 ? ` <span style="color: #10b981; font-size: 0.9rem;">+${newRolesCount}</span>` : ''}`;
        
        document.getElementById('guildOwner').textContent = guildData.ownerName || 'Inconnu';
        document.getElementById('guildRegion').textContent = guildData.region || 'Automatique';
        
        if (guildData.createdAt) {
            const createdDate = new Date(guildData.createdAt);
            document.getElementById('guildCreated').textContent = createdDate.toLocaleDateString('fr-FR');
        }
        
        await loadNewMembers();
        await loadRecentBans();
    } catch (error) {
        console.error('Erreur lors du chargement du serveur:', error);
        alert('Erreur lors du chargement des informations du serveur');
    }
}

async function loadGuildBans() {
    const bansContainer = document.getElementById('bansContainer');
    bansContainer.innerHTML = '<p class="loading">Chargement des bans...</p>';
    
    try {
        const bans = await getGuildBans(currentGuildId);
        
        if (!bans || bans.length === 0) {
            bansContainer.innerHTML = `
                <div style="text-align: center; padding: 3rem; opacity: 0.6;">
                    <i class="fas fa-check-circle" style="font-size: 3rem; color: var(--success-color); margin-bottom: 1rem;"></i>
                    <p style="font-size: 1.1rem;">Aucun ban actif sur ce serveur</p>
                </div>
            `;
            return;
        }
        
        bansContainer.innerHTML = '';
        const bansList = document.createElement('div');
        bansList.className = 'bans-list';
        bansList.style.display = 'grid';
        bansList.style.gridTemplateColumns = 'repeat(auto-fill, minmax(300px, 1fr))';
        bansList.style.gap = '1rem';
        
        bans.forEach(ban => {
            const banItem = document.createElement('div');
            banItem.className = 'ban-item';
            banItem.style.padding = '1rem';
            banItem.style.background = 'rgba(220, 38, 38, 0.1)';
            banItem.style.border = '1px solid rgba(220, 38, 38, 0.3)';
            banItem.style.borderRadius = '8px';
            banItem.style.display = 'flex';
            banItem.style.alignItems = 'center';
            banItem.style.gap = '1rem';
            banItem.style.justifyContent = 'space-between';
            
            const avatarUrl = ban.avatar || 'https://cdn.discordapp.com/embed/avatars/0.png';
            
            banItem.innerHTML = `
                <div style="display: flex; align-items: center; gap: 1rem; flex: 1;">
                    <div style="width: 40px; height: 40px; border-radius: 50%; overflow: hidden;">
                        <img src="${avatarUrl}" alt="${ban.username}" style="width: 100%; height: 100%; object-fit: cover;">
                    </div>
                    <div>
                        <h4 style="margin: 0; font-size: 1rem;">${ban.username}#${ban.discriminator}</h4>
                        <p style="margin: 0; font-size: 0.85rem; opacity: 0.7;">${ban.reason}</p>
                    </div>
                </div>
                <button class="btn btn-danger" onclick="handleUnban('${ban.user_id}', '${ban.username}')" style="white-space: nowrap;">
                    <i class="fas fa-user-check"></i> Débannir
                </button>
            `;
            bansList.appendChild(banItem);
        });
        
        bansContainer.appendChild(bansList);
    } catch (error) {
        console.error('Erreur lors du chargement des bans:', error);
        bansContainer.innerHTML = `
            <div style="text-align: center; padding: 2rem; background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px;">
                <i class="fas fa-exclamation-triangle" style="font-size: 2rem; color: var(--danger-color); margin-bottom: 1rem;"></i>
                <p style="color: var(--danger-color); font-weight: 600; margin-bottom: 0.5rem;">Erreur lors du chargement des bans</p>
                <p style="opacity: 0.7; font-size: 0.9rem;">${error.message}</p>
                <button class="btn btn-primary" onclick="loadGuildBans()" style="margin-top: 1rem;">
                    <i class="fas fa-sync"></i> Réessayer
                </button>
            </div>
        `;
    }
}

async function loadNewMembers() {
    const container = document.getElementById('newMembersContainer');
    container.innerHTML = '<p class="loading">Chargement...</p>';
    
    try {
        const members = await getGuildMembers(currentGuildId);
        
        const sevenDaysAgo = new Date();
        sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
        
        const newMembers = members.filter(m => {
            if (!m.joinedAt) return false;
            return new Date(m.joinedAt) >= sevenDaysAgo;
        });
        
        if (newMembers.length === 0) {
            container.innerHTML = '<p class="loading">Aucun nouveau membre ces 7 derniers jours</p>';
            return;
        }
        
        container.innerHTML = '';
        const membersList = document.createElement('div');
        membersList.style.display = 'flex';
        membersList.style.flexDirection = 'column';
        membersList.style.gap = '0.5rem';
        
        newMembers.slice(0, 10).forEach(member => {
            const memberName = member.username || member.name || 'Membre';
            const memberItem = document.createElement('div');
            memberItem.style.padding = '0.75rem';
            memberItem.style.background = 'rgba(16, 185, 129, 0.1)';
            memberItem.style.border = '1px solid rgba(16, 185, 129, 0.3)';
            memberItem.style.borderRadius = '6px';
            memberItem.style.display = 'flex';
            memberItem.style.alignItems = 'center';
            memberItem.style.gap = '0.75rem';
            
            const avatarUrl = member.avatar || 'https://cdn.discordapp.com/embed/avatars/0.png';
            const joinedDate = new Date(member.joinedAt);
            
            memberItem.innerHTML = `
                <div style="width: 32px; height: 32px; border-radius: 50%; overflow: hidden; flex-shrink: 0;">
                    <img src="${avatarUrl}" alt="${memberName}" style="width: 100%; height: 100%; object-fit: cover;">
                </div>
                <div style="flex: 1; min-width: 0;">
                    <div style="font-weight: 500;">${memberName}${member.bot ? ' <span style="background: #5865f2; padding: 1px 4px; border-radius: 3px; font-size: 0.7rem;">BOT</span>' : ''}</div>
                    <div style="font-size: 0.85rem; opacity: 0.7;">Rejoint le ${joinedDate.toLocaleDateString('fr-FR')}</div>
                </div>
            `;
            membersList.appendChild(memberItem);
        });
        
        if (newMembers.length > 10) {
            const moreText = document.createElement('p');
            moreText.style.textAlign = 'center';
            moreText.style.opacity = '0.7';
            moreText.style.margin = '0.5rem 0 0 0';
            moreText.textContent = `+${newMembers.length - 10} autres membres...`;
            membersList.appendChild(moreText);
        }
        
        container.appendChild(membersList);
    } catch (error) {
        console.error('Erreur:', error);
        container.innerHTML = '<p class="loading">Erreur lors du chargement</p>';
    }
}

async function loadRecentBans() {
    const container = document.getElementById('recentBansContainer');
    container.innerHTML = '<p class="loading">Chargement...</p>';
    
    try {
        const bans = await getGuildBans(currentGuildId);
        
        if (!bans || bans.length === 0) {
            container.innerHTML = '<p class="loading">Aucun ban actif</p>';
            return;
        }
        
        const recentBans = bans.slice(0, 5);
        
        container.innerHTML = '';
        const bansList = document.createElement('div');
        bansList.style.display = 'flex';
        bansList.style.flexDirection = 'column';
        bansList.style.gap = '0.5rem';
        
        recentBans.forEach(ban => {
            const banItem = document.createElement('div');
            banItem.style.padding = '0.75rem';
            banItem.style.background = 'rgba(220, 38, 38, 0.1)';
            banItem.style.border = '1px solid rgba(220, 38, 38, 0.3)';
            banItem.style.borderRadius = '6px';
            banItem.style.display = 'flex';
            banItem.style.alignItems = 'center';
            banItem.style.gap = '0.75rem';
            
            const avatarUrl = ban.avatar || 'https://cdn.discordapp.com/embed/avatars/0.png';
            
            banItem.innerHTML = `
                <div style="width: 32px; height: 32px; border-radius: 50%; overflow: hidden; flex-shrink: 0;">
                    <img src="${avatarUrl}" alt="${ban.username}" style="width: 100%; height: 100%; object-fit: cover;">
                </div>
                <div style="flex: 1; min-width: 0;">
                    <div style="font-weight: 500;">${ban.username}#${ban.discriminator}</div>
                    <div style="font-size: 0.85rem; opacity: 0.7; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${ban.reason}</div>
                </div>
            `;
            bansList.appendChild(banItem);
        });
        
        if (bans.length > 5) {
            const moreText = document.createElement('p');
            moreText.style.textAlign = 'center';
            moreText.style.opacity = '0.7';
            moreText.style.margin = '0.5rem 0 0 0';
            moreText.innerHTML = `<a href="#" onclick="event.preventDefault(); navigateToPage('bans'); document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active')); document.querySelector('[data-page=bans]').classList.add('active');" style="color: var(--primary-color); text-decoration: none;">Voir tous les bans (${bans.length})</a>`;
            bansList.appendChild(moreText);
        }
        
        container.appendChild(bansList);
    } catch (error) {
        console.error('Erreur:', error);
        container.innerHTML = '<p class="loading">Erreur lors du chargement</p>';
    }
}

async function loadGuildBans_old() {
    const bansContainer = document.getElementById('bansContainer');
    bansContainer.innerHTML = '<p class="loading">Chargement des bans...</p>';
    
    try {
        const bans = await getGuildBans(currentGuildId);
        
        if (!bans || bans.length === 0) {
            bansContainer.innerHTML = '<p class="loading">Aucun ban actif sur ce serveur</p>';
            return;
        }
        
        bansContainer.innerHTML = '';
        const bansList = document.createElement('div');
        bansList.className = 'bans-list';
        bansList.style.display = 'grid';
        bansList.style.gridTemplateColumns = 'repeat(auto-fill, minmax(300px, 1fr))';
        bansList.style.gap = '1rem';
        
        bans.forEach(ban => {
            const banItem = document.createElement('div');
            banItem.className = 'ban-item';
            banItem.style.padding = '1rem';
            banItem.style.background = 'rgba(220, 38, 38, 0.1)';
            banItem.style.border = '1px solid rgba(220, 38, 38, 0.3)';
            banItem.style.borderRadius = '8px';
            banItem.style.display = 'flex';
            banItem.style.alignItems = 'center';
            banItem.style.gap = '1rem';
            banItem.style.justifyContent = 'space-between';
            
            const avatarUrl = ban.avatar || 'https://cdn.discordapp.com/embed/avatars/0.png';
            
            banItem.innerHTML = `
                <div style="display: flex; align-items: center; gap: 1rem; flex: 1;">
                    <div style="width: 40px; height: 40px; border-radius: 50%; overflow: hidden;">
                        <img src="${avatarUrl}" alt="${ban.username}" style="width: 100%; height: 100%; object-fit: cover;">
                    </div>
                    <div>
                        <h4 style="margin: 0; font-size: 1rem;">${ban.username}#${ban.discriminator}</h4>
                        <p style="margin: 0; font-size: 0.85rem; opacity: 0.7;">${ban.reason}</p>
                    </div>
                </div>
                <button class="btn btn-danger" onclick="handleUnban('${ban.user_id}', '${ban.username}')" style="white-space: nowrap;">
                    <i class="fas fa-user-check"></i> Débannir
                </button>
            `;
            bansList.appendChild(banItem);
        });
        
        bansContainer.appendChild(bansList);
    } catch (error) {
        console.error('Erreur lors du chargement des bans:', error);
        bansContainer.innerHTML = '<p class="loading">Erreur lors du chargement des bans</p>';
    }
}

async function handleUnban(userId, username) {
    if (!confirm(`Êtes-vous sûr de vouloir débannir ${username} ?`)) {
        return;
    }
    
    try {
        await unbanUser(currentGuildId, userId);
        alert(`${username} a été débanni avec succès`);
        await loadGuildBans();
    } catch (error) {
        alert(`Erreur lors du débannissement: ${error.message}`);
    }
}

async function loadGuildLogs() {
    const logsContainer = document.getElementById('logsContainer');
    logsContainer.innerHTML = '<p class="loading">Chargement des logs...</p>';
    
    try {
        const allLogs = await getCommandLogs();
        

        const guildLogs = allLogs.filter(log => log.guild_id === currentGuildId);
        

        const today = new Date().toISOString().split('T')[0];
        const todayLogs = guildLogs.filter(log => log.timestamp.startsWith(today));
        

        const activeUsers = new Set(guildLogs.map(log => log.user));
        

        document.getElementById('totalCommandsCount').textContent = guildLogs.length;
        document.getElementById('todayCommandsCount').textContent = todayLogs.length;
        document.getElementById('errorsCount').textContent = '0'; 
        document.getElementById('activeUsersCount').textContent = activeUsers.size;
        
        if (guildLogs.length === 0) {
            logsContainer.innerHTML = '<p class="loading">Aucun log disponible pour ce serveur</p>';
            return;
        }
        

        window.currentGuildLogs = guildLogs;
        

        displayLogs(guildLogs);
    } catch (error) {
        console.error('Erreur lors du chargement des logs:', error);
        logsContainer.innerHTML = '<p class="loading">Erreur lors du chargement des logs</p>';
    }
}

function displayLogs(logs) {
    const logsContainer = document.getElementById('logsContainer');
    logsContainer.innerHTML = '';
    
    if (logs.length === 0) {
        logsContainer.innerHTML = '<p class="loading">Aucun log correspondant</p>';
        return;
    }
    
    logs.forEach(log => {
        const logItem = document.createElement('div');
        logItem.className = 'log-item';
        logItem.dataset.logType = 'command';
        

        let parametersHtml = '';
        if (log.parameters && Object.keys(log.parameters).length > 0) {
            parametersHtml = '<div class="log-parameters" style="margin-top: 0.5rem; padding: 0.5rem; background: rgba(255, 255, 255, 0.03); border-radius: 4px; font-size: 0.9rem;">';
            parametersHtml += '<i class="fas fa-cog"></i> <strong>Paramètres:</strong><br>';
            for (const [key, value] of Object.entries(log.parameters)) {
                parametersHtml += `<span style="margin-left: 1.5rem; opacity: 0.8;">• ${key}: <code style="background: rgba(255, 255, 255, 0.1); padding: 2px 6px; border-radius: 3px;">${value}</code></span><br>`;
            }
            parametersHtml += '</div>';
        }
        
        logItem.innerHTML = `
            <div class="log-header">
                <span class="log-command"><i class="fas fa-terminal"></i> /${log.command}</span>
                <span class="log-time">${new Date(log.timestamp).toLocaleString('fr-FR')}</span>
            </div>
            <div class="log-details">
                <span><i class="fas fa-user"></i> ${log.user}</span>
                ${log.channel ? `<span style="margin-left: 1rem;"><i class="fas fa-hashtag"></i> ${log.channel}</span>` : ''}
            </div>
            ${parametersHtml}
        `;
        logsContainer.appendChild(logItem);
    });
}

function filterLogs() {
    if (!window.currentGuildLogs) return;
    
    const searchTerm = document.getElementById('logSearch').value.toLowerCase();
    const typeFilter = document.getElementById('logTypeFilter').value;
    
    let filteredLogs = window.currentGuildLogs;
    

    if (searchTerm) {
        filteredLogs = filteredLogs.filter(log => 
            log.command.toLowerCase().includes(searchTerm) ||
            log.user.toLowerCase().includes(searchTerm) ||
            (log.channel && log.channel.toLowerCase().includes(searchTerm))
        );
    }
    

    
    displayLogs(filteredLogs);
}

function downloadGuildLogs() {
    if (!window.currentGuildLogs || window.currentGuildLogs.length === 0) {
        alert('Aucun log à télécharger');
        return;
    }
    
    let csvContent = 'Date,Commande,Utilisateur,Canal,Paramètres\n';
    
    window.currentGuildLogs.forEach(log => {
        const date = new Date(log.timestamp).toLocaleString('fr-FR');
        const command = log.command;
        const user = log.user;
        const channel = log.channel || 'N/A';
        const params = log.parameters ? JSON.stringify(log.parameters) : 'N/A';
        
        csvContent += `"${date}","${command}","${user}","${channel}","${params}"\n`;
    });
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `logs-${currentGuildId}-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

function showUserProfile() {
    if (!discordUser) return;
    
    const modal = document.createElement('div');
    modal.id = 'profileModal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
    `;
    
    const isAnimated = discordUser.avatar && discordUser.avatar.startsWith('a_');
    const extension = isAnimated ? 'gif' : 'png';
    const avatarUrl = discordUser.avatar 
        ? `https://cdn.discordapp.com/avatars/${discordUser.id}/${discordUser.avatar}.${extension}?size=512`
        : 'https://cdn.discordapp.com/embed/avatars/0.png';
    
    modal.innerHTML = `
        <div style="
            background: var(--card-bg);
            padding: 2rem;
            border-radius: 12px;
            max-width: 400px;
            width: 90%;
            text-align: center;
            position: relative;
        ">
            <button onclick="this.closest('#profileModal').remove()" style="
                position: absolute;
                top: 10px;
                right: 10px;
                background: var(--danger-color);
                border: none;
                color: white;
                width: 30px;
                height: 30px;
                border-radius: 50%;
                cursor: pointer;
                font-size: 18px;
            ">×</button>
            <img src="${avatarUrl}" alt="Avatar" style="
                width: 200px;
                height: 200px;
                border-radius: 50%;
                margin-bottom: 1rem;
                border: 4px solid var(--primary-color);
            ">
            <h2 style="color: var(--primary-color); margin-bottom: 0.5rem;">${discordUser.username}</h2>
            <p style="color: var(--text-secondary); margin-bottom: 1rem;">ID: ${discordUser.id}</p>
            <p style="color: var(--text-secondary); margin-bottom: 1rem;">
                <i class="fas fa-calendar-alt"></i> Compte créé le: ${new Date(parseInt(discordUser.id) / 4194304 + 1420070400000).toLocaleDateString('fr-FR', { year: 'numeric', month: 'long', day: 'numeric' })}
            </p>
            <div style="margin-top: 1.5rem; display: flex; gap: 1rem; justify-content: center;">
                <a href="https://discord.com/users/${discordUser.id}" target="_blank" class="btn btn-primary" style="text-decoration: none; display: inline-block;">
                    <i class="fas fa-external-link-alt"></i> Voir sur Discord
                </a>
            </div>
        </div>
    `;
    
    modal.onclick = (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    };
    
    document.body.appendChild(modal);
}

async function loadGuildMembers() {
    const membersContainer = document.getElementById('membersContainer');
    membersContainer.innerHTML = '<p class="loading">Chargement des membres...</p>';
    
    try {
        const members = await getGuildMembers(currentGuildId);
        
        if (!members || members.length === 0) {
            membersContainer.innerHTML = '<p class="loading">Aucun membre trouvé</p>';
            return;
        }
        
        membersContainer.innerHTML = '';
        const membersList = document.createElement('div');
        membersList.className = 'members-list';
        membersList.style.display = 'grid';
        membersList.style.gridTemplateColumns = 'repeat(auto-fill, minmax(250px, 1fr))';
        membersList.style.gap = '1rem';
        
        members.forEach(member => {
            const memberName = member.username || member.name || 'Membre';
            const memberItem = document.createElement('div');
            memberItem.className = 'member-item';
            memberItem.style.padding = '1rem';
            memberItem.style.background = 'rgba(255, 255, 255, 0.05)';
            memberItem.style.borderRadius = '8px';
            memberItem.style.display = 'flex';
            memberItem.style.alignItems = 'center';
            memberItem.style.gap = '1rem';
            memberItem.style.cursor = 'pointer';
            memberItem.style.transition = 'all 0.2s ease';
            
            memberItem.onclick = () => showMemberDetails(member);
            
            memberItem.onmouseenter = () => {
                memberItem.style.background = 'rgba(255, 255, 255, 0.1)';
                memberItem.style.transform = 'scale(1.02)';
            };
            memberItem.onmouseleave = () => {
                memberItem.style.background = 'rgba(255, 255, 255, 0.05)';
                memberItem.style.transform = 'scale(1)';
            };
            

            const CREATOR_ID = '790617995625758730';
            const isCreator = member.id === CREATOR_ID;
            
            memberItem.innerHTML = `
                <div class="member-avatar" style="width: 40px; height: 40px; border-radius: 50%; background: #5865f2; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; font-weight: bold; overflow: hidden;">
                    ${member.avatar ? `<img src="${member.avatar}" alt="${memberName}" style="width: 100%; height: 100%; object-fit: cover;">` : memberName.charAt(0).toUpperCase()}
                </div>
                <div class="member-info" style="flex: 1;">
                    <h4 style="margin: 0; font-size: 1rem;">
                        ${memberName}
                        ${member.bot ? ' <span style="background: #5865f2; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem;">BOT</span>' : ''}
                        ${isCreator ? ' <span style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 600;" title="Créateur du bot">✨ CRÉATEUR</span>' : ''}
                    </h4>
                    <p style="margin: 0; font-size: 0.85rem; opacity: 0.7;">${member.discriminator ? `#${member.discriminator}` : ''}</p>
                </div>
            `;
            membersList.appendChild(memberItem);
        });
        
        membersContainer.appendChild(membersList);
    } catch (error) {
        console.error('Erreur lors du chargement des membres:', error);
        membersContainer.innerHTML = `<p class="loading">Erreur lors du chargement des membres: ${error.message}</p>`;
    }
}

function showMemberDetails(member) {
    const memberName = member.username || member.name || 'Membre';
    const avatarUrl = member.avatar || 'https://cdn.discordapp.com/embed/avatars/0.png';
    

    const createdDate = member.createdAt ? new Date(member.createdAt) : new Date(parseInt(member.id) / 4194304 + 1420070400000);
    const joinedDate = member.joinedAt ? new Date(member.joinedAt) : null;
    

    const modal = document.createElement('div');
    modal.id = 'memberModal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
    `;
    
    modal.innerHTML = `
        <div style="
            background: var(--card-bg);
            padding: 2rem;
            border-radius: 12px;
            max-width: 500px;
            width: 90%;
            position: relative;
        ">
            <button onclick="this.closest('#memberModal').remove()" style="
                position: absolute;
                top: 10px;
                right: 10px;
                background: var(--danger-color);
                border: none;
                color: white;
                width: 30px;
                height: 30px;
                border-radius: 50%;
                cursor: pointer;
                font-size: 18px;
            ">×</button>
            
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <img src="${avatarUrl}" alt="Avatar" style="
                    width: 120px;
                    height: 120px;
                    border-radius: 50%;
                    margin-bottom: 1rem;
                    border: 4px solid var(--primary-color);
                ">
                <h2 style="color: var(--primary-color); margin-bottom: 0.5rem;">${memberName}${member.bot ? ' <span style="background: #5865f2; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem;">BOT</span>' : ''}</h2>
                <p style="color: var(--text-secondary); margin-bottom: 0.5rem;">${member.discriminator ? `#${member.discriminator}` : ''}</p>
                <p style="color: var(--text-secondary); font-size: 0.9rem;">ID: ${member.id}</p>
            </div>
            
            <div style="margin-bottom: 1.5rem;">
                <div style="margin-bottom: 1rem; padding: 0.75rem; background: rgba(255, 255, 255, 0.05); border-radius: 8px;">
                    <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">
                        <i class="fas fa-calendar-plus"></i> Compte créé le
                    </p>
                    <p style="margin: 0.25rem 0 0 0; font-weight: bold;">
                        ${createdDate.toLocaleDateString('fr-FR', { year: 'numeric', month: 'long', day: 'numeric' })}
                    </p>
                </div>
                
                ${joinedDate ? `
                <div style="margin-bottom: 1rem; padding: 0.75rem; background: rgba(255, 255, 255, 0.05); border-radius: 8px;">
                    <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">
                        <i class="fas fa-sign-in-alt"></i> A rejoint le serveur le
                    </p>
                    <p style="margin: 0.25rem 0 0 0; font-weight: bold;">
                        ${joinedDate.toLocaleDateString('fr-FR', { year: 'numeric', month: 'long', day: 'numeric' })}
                    </p>
                </div>
                ` : ''}
            </div>
            

            
            <div style="margin-top: 1.5rem; display: flex; gap: 1rem; justify-content: center;">
                <a href="https://discord.com/users/${member.id}" target="_blank" class="btn btn-primary" style="text-decoration: none; display: inline-block;">
                    <i class="fas fa-external-link-alt"></i> Voir sur Discord
                </a>
            </div>
        </div>
    `;
    
    modal.onclick = (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    };
    
    document.body.appendChild(modal);
}

async function loadGuildBlacklist() {
    const blacklistContainer = document.getElementById('blacklistContainer');
    blacklistContainer.innerHTML = '<p class="loading">Chargement de la blacklist...</p>';
    
    try {
        const blacklist = await getGuildBlacklist(currentGuildId);
        
        if (!blacklist || Object.keys(blacklist).length === 0) {
            blacklistContainer.innerHTML = `
                <div style="text-align: center; padding: 3rem; opacity: 0.6;">
                    <i class="fas fa-shield-alt" style="font-size: 3rem; color: var(--success-color); margin-bottom: 1rem;"></i>
                    <p style="font-size: 1.1rem;">Aucun utilisateur dans la blacklist</p>
                </div>
            `;
            return;
        }
        
        blacklistContainer.innerHTML = '';
        const blacklistList = document.createElement('div');
        blacklistList.className = 'blacklist-list';
        blacklistList.style.display = 'grid';
        blacklistList.style.gridTemplateColumns = 'repeat(auto-fill, minmax(350px, 1fr))';
        blacklistList.style.gap = '1rem';
        
        for (const [userId, userDataOrReason] of Object.entries(blacklist)) {
            let username, discriminator, avatar, reason, addedAt;
            
            if (typeof userDataOrReason === 'string') {
                reason = userDataOrReason;
                username = 'Utilisateur';
                discriminator = '????';
                avatar = null;
                addedAt = null;
            } else {
                username = userDataOrReason.username || 'Utilisateur inconnu';
                discriminator = userDataOrReason.discriminator || '0000';
                avatar = userDataOrReason.avatar;
                reason = userDataOrReason.reason || 'Aucune raison fournie';
                addedAt = userDataOrReason.added_at;
            }
            
            const blacklistItem = document.createElement('div');
            blacklistItem.className = 'blacklist-item';
            blacklistItem.style.padding = '1.25rem';
            blacklistItem.style.background = 'rgba(220, 38, 38, 0.1)';
            blacklistItem.style.border = '1px solid rgba(220, 38, 38, 0.3)';
            blacklistItem.style.borderRadius = '8px';
            blacklistItem.style.display = 'flex';
            blacklistItem.style.flexDirection = 'column';
            blacklistItem.style.gap = '1rem';
            
            const avatarUrl = avatar || 'https://cdn.discordapp.com/embed/avatars/0.png';
            
            let dateInfo = '';
            if (addedAt) {
                const date = new Date(addedAt);
                dateInfo = `<div style="font-size: 0.85rem; opacity: 0.6; margin-top: 0.25rem;">Ajouté le ${date.toLocaleDateString('fr-FR')}</div>`;
            }
            
            blacklistItem.innerHTML = `
                <div style="display: flex; align-items: center; gap: 1rem; flex: 1;">
                    <div style="width: 50px; height: 50px; border-radius: 50%; overflow: hidden; flex-shrink: 0; border: 2px solid rgba(220, 38, 38, 0.5);">
                        <img src="${avatarUrl}" alt="${username}" style="width: 100%; height: 100%; object-fit: cover;">
                    </div>
                    <div style="flex: 1; min-width: 0;">
                        <h4 style="margin: 0; font-size: 1.05rem; margin-bottom: 0.25rem;">${username}#${discriminator}</h4>
                        <p style="margin: 0; font-size: 0.85rem; opacity: 0.7;">ID: ${userId}</p>
                        ${dateInfo}
                    </div>
                </div>
                <div style="padding: 0.75rem; background: rgba(0, 0, 0, 0.2); border-radius: 6px;">
                    <div style="font-size: 0.85rem; opacity: 0.7; margin-bottom: 0.25rem;">Raison:</div>
                    <div style="word-break: break-word;">${reason}</div>
                </div>
                <button class="btn btn-primary" onclick="removeFromBlacklist('${userId}')" style="width: 100%;">
                    <i class="fas fa-user-check"></i> Retirer de la blacklist
                </button>
            `;
            blacklistList.appendChild(blacklistItem);
        }
        
        blacklistContainer.appendChild(blacklistList);
    } catch (error) {
        console.error('Erreur lors du chargement de la blacklist:', error);
        blacklistContainer.innerHTML = `
            <div style="text-align: center; padding: 2rem; background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px;">
                <i class="fas fa-exclamation-triangle" style="font-size: 2rem; color: var(--danger-color); margin-bottom: 1rem;"></i>
                <p style="color: var(--danger-color); font-weight: 600; margin-bottom: 0.5rem;">Erreur lors du chargement de la blacklist</p>
                <p style="opacity: 0.7; font-size: 0.9rem;">${error.message}</p>
                <button class="btn btn-primary" onclick="loadGuildBlacklist()" style="margin-top: 1rem;">
                    <i class="fas fa-sync"></i> Réessayer
                </button>
            </div>
        `;
    }
}

async function addToBlacklist() {
    const userIdInput = document.getElementById('blacklistUserId');
    const reasonInput = document.getElementById('blacklistReason');
    
    const userId = userIdInput.value.trim();
    const reason = reasonInput.value.trim() || 'Aucune raison fournie';
    
    if (!userId) {
        alert('Veuillez entrer un ID utilisateur');
        return;
    }
    
    if (!/^\d+$/.test(userId)) {
        alert('L\'ID utilisateur doit contenir uniquement des chiffres');
        return;
    }
    
    try {
        await addUserToBlacklist(currentGuildId, userId, reason);
        alert(`L'utilisateur ${userId} a été ajouté à la blacklist`);
        
        userIdInput.value = '';
        reasonInput.value = '';
        
        await loadGuildBlacklist();
    } catch (error) {
        alert(`Erreur lors de l'ajout à la blacklist: ${error.message}`);
    }
}

async function removeFromBlacklist(userId) {
    if (!confirm(`Êtes-vous sûr de vouloir retirer l'utilisateur ${userId} de la blacklist ?`)) {
        return;
    }
    
    try {
        await removeUserFromBlacklist(currentGuildId, userId);
        alert(`L'utilisateur ${userId} a été retiré de la blacklist`);
        await loadGuildBlacklist();
    } catch (error) {
        alert(`Erreur lors du retrait de la blacklist: ${error.message}`);
    }
}

async function addBan() {
    const userIdInput = document.getElementById('banUserId');
    const reasonInput = document.getElementById('banReason');
    
    const userId = userIdInput.value.trim();
    const reason = reasonInput.value.trim() || 'Aucune raison fournie';
    
    if (!userId) {
        alert('Veuillez entrer un ID utilisateur');
        return;
    }
    
    if (!/^\d+$/.test(userId)) {
        alert('L\'ID utilisateur doit contenir uniquement des chiffres');
        return;
    }
    
    if (!confirm(`Êtes-vous sûr de vouloir bannir l'utilisateur ${userId} ?\nRaison: ${reason}`)) {
        return;
    }
    
    try {
        await banUser(currentGuildId, userId, reason);
        alert(`L'utilisateur ${userId} a été banni avec succès`);
        
        userIdInput.value = '';
        reasonInput.value = '';
        
        await loadGuildBans();
    } catch (error) {
        alert(`Erreur lors du bannissement: ${error.message}`);
    }
}



async function loadGuildSettings() {
    try {
        const response = await fetch(`/api/guilds/${currentGuildId}/settings`);
        const settings = await response.json();
        
        document.getElementById('commandPrefix').value = settings.prefix || '!';
        document.getElementById('languageSetting').value = settings.language || 'fr';
        document.getElementById('autoMod').checked = settings.auto_mod || false;
        
        document.getElementById('welcomeEnabled').checked = settings.welcome_enabled || false;
        
        if (guildData && guildData.channels) {
            const textChannels = guildData.channels.filter(c => c.type === 'text' || c.type.includes('text'));
            
            const logChannelSelect = document.getElementById('logChannel');
            const welcomeChannelSelect = document.getElementById('welcomeChannel');
            
            logChannelSelect.innerHTML = '<option value="">Sélectionner un canal...</option>';
            welcomeChannelSelect.innerHTML = '<option value="">Sélectionner un canal...</option>';
            
            textChannels.forEach(channel => {
                const option1 = document.createElement('option');
                option1.value = channel.id;
                option1.textContent = `# ${channel.name}`;
                logChannelSelect.appendChild(option1);
                
                const option2 = document.createElement('option');
                option2.value = channel.id;
                option2.textContent = `# ${channel.name}`;
                welcomeChannelSelect.appendChild(option2);
            });
            
            if (settings.log_channel) {
                logChannelSelect.value = settings.log_channel;
            }
            if (settings.welcome_channel) {
                welcomeChannelSelect.value = settings.welcome_channel;
            }
        }
        
        if (guildData && guildData.roles) {
            const modRoleSelect = document.getElementById('modRole');
            const autoRoleSelect = document.getElementById('autoRole');
            
            modRoleSelect.innerHTML = '<option value="">Sélectionner un rôle...</option>';
            autoRoleSelect.innerHTML = '<option value="">Aucun rôle automatique</option>';
            
            const roles = guildData.roles.filter(r => r.name !== '@everyone');
            
            roles.forEach(role => {
                const option = document.createElement('option');
                option.value = role.id;
                option.textContent = role.name;
                modRoleSelect.appendChild(option);
                
                const option2 = document.createElement('option');
                option2.value = role.id;
                option2.textContent = role.name;
                autoRoleSelect.appendChild(option2);
            });
            
            if (settings.mod_role) {
                modRoleSelect.value = settings.mod_role;
            }
            if (settings.auto_role) {
                autoRoleSelect.value = settings.auto_role;
            }
        }
        
        document.getElementById('settingsSaveStatus').innerHTML = '<i class="fas fa-info-circle"></i> Paramètres chargés';
    } catch (error) {
        console.error('Erreur lors du chargement des paramètres:', error);
        document.getElementById('settingsSaveStatus').innerHTML = '<i class="fas fa-exclamation-triangle"></i> Erreur lors du chargement des paramètres';
    }
}

async function saveGuildSettings() {
    try {
        const settings = {
            prefix: document.getElementById('commandPrefix').value || '!',
            language: document.getElementById('languageSetting').value || 'fr',
            log_channel: document.getElementById('logChannel').value || null,
            welcome_enabled: document.getElementById('welcomeEnabled').checked,
            welcome_channel: document.getElementById('welcomeChannel').value || null,
            auto_role: document.getElementById('autoRole').value || null,
            auto_mod: document.getElementById('autoMod').checked,
            mod_role: document.getElementById('modRole').value || null
        };
        
        const response = await fetch(addTokenToUrl(`/api/guilds/${currentGuildId}/settings`), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        });
        
        if (response.ok) {
            document.getElementById('settingsSaveStatus').innerHTML = '<i class="fas fa-check-circle" style="color: #10B981;"></i> Paramètres sauvegardés avec succès !';
            setTimeout(() => {
                document.getElementById('settingsSaveStatus').innerHTML = '';
            }, 3000);
        } else {
            const error = await response.json();
            document.getElementById('settingsSaveStatus').innerHTML = `<i class="fas fa-exclamation-circle" style="color: #EF4444;"></i> Erreur: ${error.error}`;
        }
    } catch (error) {
        console.error('Erreur lors de la sauvegarde:', error);
        document.getElementById('settingsSaveStatus').innerHTML = `<i class="fas fa-exclamation-circle" style="color: #EF4444;"></i> Erreur: ${error.message}`;
    }
}

async function resetGuildSettings() {
    if (!confirm('Êtes-vous sûr de vouloir réinitialiser tous les paramètres aux valeurs par défaut ?')) {
        return;
    }
    
    try {
        const response = await fetch(addTokenToUrl(`/api/guilds/${currentGuildId}/settings`), {
            method: 'DELETE'
        });
        
        if (response.ok) {
            document.getElementById('settingsSaveStatus').innerHTML = '<i class="fas fa-check-circle" style="color: #10B981;"></i> Paramètres réinitialisés !';
            await loadGuildSettings();
        } else {
            const error = await response.json();
            document.getElementById('settingsSaveStatus').innerHTML = `<i class="fas fa-exclamation-circle" style="color: #EF4444;"></i> Erreur: ${error.error}`;
        }
    } catch (error) {
        console.error('Erreur lors de la réinitialisation:', error);
        document.getElementById('settingsSaveStatus').innerHTML = `<i class="fas fa-exclamation-circle" style="color: #EF4444;"></i> Erreur: ${error.message}`;
    }
}


let currentTicketsData = null;

async function loadTicketsPage() {
    await loadTicketConfig();
    await loadTicketStats();
    await loadTicketsList();
}

async function loadTicketConfig() {
    try {
        const response = await fetch(addTokenToUrl(`/api/guilds/${currentGuildId}/tickets/config`));
        const config = await response.json();
        
        if (guildData) {
            const ticketChannelSelect = document.getElementById('ticketChannel');
            ticketChannelSelect.innerHTML = '<option value="">Sélectionner un canal...</option>';
            
            const textChannels = guildData.channels.filter(c => c.type === 'text' || c.type.includes('text'));
            textChannels.forEach(channel => {
                const option = document.createElement('option');
                option.value = channel.id;
                option.textContent = `# ${channel.name}`;
                if (config.ticket_channel && channel.id === config.ticket_channel) {
                    option.selected = true;
                }
                ticketChannelSelect.appendChild(option);
            });
            
            const categories = guildData.channels.filter(c => c.type === 'category' || c.type.includes('category'));
            
            const ticketCategorySelect = document.getElementById('ticketCategory');
            const archiveCategorySelect = document.getElementById('archiveCategory');
            
            ticketCategorySelect.innerHTML = '<option value="">Sélectionner une catégorie...</option>';
            archiveCategorySelect.innerHTML = '<option value="">Sélectionner une catégorie...</option>';
            
            categories.forEach(category => {
                const option1 = document.createElement('option');
                option1.value = category.id;
                option1.textContent = category.name;
                if (config.ticket_category && category.id === config.ticket_category) {
                    option1.selected = true;
                }
                ticketCategorySelect.appendChild(option1);
                
                const option2 = document.createElement('option');
                option2.value = category.id;
                option2.textContent = category.name;
                if (config.archive_category && category.id === config.archive_category) {
                    option2.selected = true;
                }
                archiveCategorySelect.appendChild(option2);
            });
            
            const supportRolesSelect = document.getElementById('supportRoles');
            supportRolesSelect.innerHTML = '';
            
            const roles = guildData.roles.filter(r => r.name !== '@everyone');
            roles.forEach(role => {
                const option = document.createElement('option');
                option.value = role.id;
                option.textContent = role.name;
                if (config.ticket_support_roles && config.ticket_support_roles.includes(role.id)) {
                    option.selected = true;
                }
                supportRolesSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Erreur lors du chargement de la config tickets:', error);
        document.getElementById('ticketConfigStatus').innerHTML = `<i class="fas fa-exclamation-circle" style="color: #EF4444;"></i> Erreur: ${error.message}`;
    }
}

async function saveTicketConfig() {
    try {
        const ticketChannel = document.getElementById('ticketChannel').value;
        const ticketCategory = document.getElementById('ticketCategory').value;
        const archiveCategory = document.getElementById('archiveCategory').value;
        const supportRoles = Array.from(document.getElementById('supportRoles').selectedOptions).map(opt => opt.value);
        
        const config = {
            ticket_channel: ticketChannel || null,
            ticket_category: ticketCategory || null,
            archive_category: archiveCategory || null,
            ticket_support_roles: supportRoles
        };
        
        const response = await fetch(addTokenToUrl(`/api/guilds/${currentGuildId}/tickets/config`), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        if (response.ok) {
            document.getElementById('ticketConfigStatus').innerHTML = '<i class="fas fa-check-circle" style="color: #10B981;"></i> Configuration sauvegardée avec succès !';
            setTimeout(() => {
                document.getElementById('ticketConfigStatus').innerHTML = '';
            }, 3000);
        } else {
            const error = await response.json();
            document.getElementById('ticketConfigStatus').innerHTML = `<i class="fas fa-exclamation-circle" style="color: #EF4444;"></i> Erreur: ${error.error}`;
        }
    } catch (error) {
        console.error('Erreur lors de la sauvegarde:', error);
        document.getElementById('ticketConfigStatus').innerHTML = `<i class="fas fa-exclamation-circle" style="color: #EF4444;"></i> Erreur: ${error.message}`;
    }
}

async function sendTicketPanel() {
    if (!confirm('Voulez-vous envoyer le panel de création de tickets dans le canal configuré ?')) {
        return;
    }
    
    try {
        const response = await fetch(addTokenToUrl(`/api/guilds/${currentGuildId}/tickets/panel`), {
            method: 'POST'
        });
        
        if (response.ok) {
            document.getElementById('ticketConfigStatus').innerHTML = '<i class="fas fa-check-circle" style="color: #10B981;"></i> Panel de tickets envoyé avec succès !';
            setTimeout(() => {
                document.getElementById('ticketConfigStatus').innerHTML = '';
            }, 3000);
        } else {
            const error = await response.json();
            document.getElementById('ticketConfigStatus').innerHTML = `<i class="fas fa-exclamation-circle" style="color: #EF4444;"></i> Erreur: ${error.error}`;
        }
    } catch (error) {
        console.error('Erreur lors de l\'envoi du panel:', error);
        document.getElementById('ticketConfigStatus').innerHTML = `<i class="fas fa-exclamation-circle" style="color: #EF4444;"></i> Erreur: ${error.message}`;
    }
}

async function loadTicketStats() {
    try {
        const response = await fetch(addTokenToUrl(`/api/guilds/${currentGuildId}/tickets`));
        const data = await response.json();
        
        currentTicketsData = data;
        
        document.getElementById('totalTickets').textContent = data.total || 0;
        document.getElementById('openTickets').textContent = data.open || 0;
        document.getElementById('closedTickets').textContent = data.closed || 0;
        
        if (data.tickets && data.tickets.length > 0) {
            const closedTickets = data.tickets.filter(t => t.status === 'closed' && t.closed_at && t.created_at);
            if (closedTickets.length > 0) {
                const avgTime = closedTickets.reduce((sum, ticket) => {
                    const created = new Date(ticket.created_at);
                    const closed = new Date(ticket.closed_at);
                    return sum + (closed - created);
                }, 0) / closedTickets.length;
                
                const hours = Math.floor(avgTime / (1000 * 60 * 60));
                const minutes = Math.floor((avgTime % (1000 * 60 * 60)) / (1000 * 60));
                document.getElementById('avgResponseTime').textContent = `${hours}h ${minutes}m`;
            }
        }
    } catch (error) {
        console.error('Erreur lors du chargement des stats tickets:', error);
    }
}

async function refreshTicketStats() {
    await loadTicketStats();
    await loadTicketsList();
    document.getElementById('ticketConfigStatus').innerHTML = '<i class="fas fa-check-circle" style="color: #10B981;"></i> Statistiques actualisées !';
    setTimeout(() => {
        document.getElementById('ticketConfigStatus').innerHTML = '';
    }, 2000);
}

async function loadTicketsList() {
    const container = document.getElementById('ticketsListContainer');
    container.innerHTML = '<p class="loading">Chargement des tickets...</p>';
    
    try {
        const response = await fetch(addTokenToUrl(`/api/guilds/${currentGuildId}/tickets`));
        const data = await response.json();
        
        currentTicketsData = data;
        
        if (!data.tickets || data.tickets.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 3rem; opacity: 0.6;">
                    <i class="fas fa-ticket-alt" style="font-size: 3rem; color: var(--primary-color); margin-bottom: 1rem;"></i>
                    <p style="font-size: 1.1rem;">Aucun ticket créé pour le moment</p>
                    <small>Les tickets apparaîtront ici une fois créés par les utilisateurs</small>
                </div>
            `;
            return;
        }
        
        displayTickets(data.tickets);
    } catch (error) {
        console.error('Erreur lors du chargement des tickets:', error);
        container.innerHTML = `
            <div style="text-align: center; padding: 2rem; background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px;">
                <i class="fas fa-exclamation-triangle" style="font-size: 2rem; color: var(--danger-color); margin-bottom: 1rem;"></i>
                <p style="color: var(--danger-color); font-weight: 600;">Erreur lors du chargement des tickets</p>
                <p style="opacity: 0.7; font-size: 0.9rem;">${error.message}</p>
            </div>
        `;
    }
}

function displayTickets(tickets) {
    const container = document.getElementById('ticketsListContainer');
    container.innerHTML = '';
    
    if (tickets.length === 0) {
        container.innerHTML = '<p class="loading">Aucun ticket correspondant</p>';
        return;
    }
    
    const ticketsList = document.createElement('div');
    ticketsList.style.display = 'grid';
    ticketsList.style.gridTemplateColumns = 'repeat(auto-fill, minmax(350px, 1fr))';
    ticketsList.style.gap = '1rem';
    
    tickets.slice(0, 50).forEach(ticket => {
        const ticketCard = document.createElement('div');
        ticketCard.style.cssText = `
            background: var(--card-bg);
            padding: 1.5rem;
            border-radius: 12px;
            border: 2px solid ${ticket.status === 'open' ? '#F59E0B' : '#10B981'};
            transition: all 0.3s ease;
            cursor: pointer;
        `;
        
        ticketCard.onmouseenter = () => {
            ticketCard.style.transform = 'translateY(-4px)';
            ticketCard.style.boxShadow = `0 8px 20px ${ticket.status === 'open' ? 'rgba(245, 158, 11, 0.3)' : 'rgba(16, 185, 129, 0.3)'}`;
        };
        ticketCard.onmouseleave = () => {
            ticketCard.style.transform = 'translateY(0)';
            ticketCard.style.boxShadow = 'none';
        };
        
        const statusBadge = ticket.status === 'open' 
            ? '<span style="background: #F59E0B; color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.85rem; font-weight: 600;">🔓 Ouvert</span>'
            : '<span style="background: #10B981; color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.85rem; font-weight: 600;">✅ Fermé</span>';
        
        const priorityConfig = {
            urgent: { label: '🔴 URGENT', color: '#EF4444', bg: 'rgba(239, 68, 68, 0.1)' },
            high: { label: '🔶 Élevé', color: '#F59E0B', bg: 'rgba(245, 158, 11, 0.1)' },
            normal: { label: '🟢 Normal', color: '#10B981', bg: 'rgba(16, 185, 129, 0.1)' },
            low: { label: '🔵 Faible', color: '#3B82F6', bg: 'rgba(59, 130, 246, 0.1)' }
        };
        const priority = ticket.priority || 'normal';
        const priorityInfo = priorityConfig[priority] || priorityConfig.normal;
        const priorityBadge = `<span style="background: ${priorityInfo.bg}; color: ${priorityInfo.color}; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.85rem; font-weight: 600; border: 1px solid ${priorityInfo.color};">${priorityInfo.label}</span>`;
        
        const createdDate = new Date(ticket.created_at || Date.now());
        const closedDate = ticket.closed_at ? new Date(ticket.closed_at) : null;
        
        let claimedBy = null;
        let joinedBy = [];
        if (ticket.notes && Array.isArray(ticket.notes)) {
            const claimNote = ticket.notes.find(n => n.type === 'claim');
            if (claimNote && claimNote.by) {
                claimedBy = claimNote.by;
            }
            joinedBy = ticket.notes.filter(n => n.type === 'join').map(n => n.name || n.user_id);
        }
        
        ticketCard.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                <div style="flex: 1;">
                    <h4 style="margin: 0 0 0.5rem 0; color: var(--primary-color); font-size: 1.1rem;">
                        🎫 Ticket #${ticket.ticket_id || 'N/A'}
                    </h4>
                    <p style="margin: 0; opacity: 0.7; font-size: 0.9rem;">
                        ${ticket.subject || 'Sans sujet'}
                    </p>
                </div>
                <div style="display: flex; flex-direction: column; gap: 0.5rem; align-items: flex-end;">
                    ${statusBadge}
                    ${priorityBadge}
                </div>
            </div>
            
            <div style="margin-bottom: 1rem; padding: 1rem; background: rgba(255, 255, 255, 0.03); border-radius: 8px;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <i class="fas fa-user" style="opacity: 0.7;"></i>
                    <span style="font-weight: 500;">${ticket.user_name || 'Utilisateur inconnu'}</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem; opacity: 0.7; font-size: 0.9rem;">
                    <i class="fas fa-calendar"></i>
                    <span>Créé le ${createdDate.toLocaleDateString('fr-FR')} à ${createdDate.toLocaleTimeString('fr-FR', {hour: '2-digit', minute: '2-digit'})}</span>
                </div>
                ${closedDate ? `
                <div style="display: flex; align-items: center; gap: 0.5rem; opacity: 0.7; font-size: 0.9rem; margin-top: 0.25rem;">
                    <i class="fas fa-check-circle"></i>
                    <span>Fermé le ${closedDate.toLocaleDateString('fr-FR')} à ${closedDate.toLocaleTimeString('fr-FR', {hour: '2-digit', minute: '2-digit'})}</span>
                </div>
                ` : ''}
                ${claimedBy ? `
                <div style="display: flex; align-items: center; gap: 0.5rem; opacity: 0.7; font-size: 0.9rem; margin-top: 0.25rem;">
                    <i class="fas fa-user-check" style="color: #10B981;"></i>
                    <span>Pris en charge par <strong style="color: #10B981;">&lt;@${claimedBy}&gt;</strong></span>
                </div>
                ` : ''}
                ${joinedBy.length > 0 ? `
                <div style="display: flex; align-items: center; gap: 0.5rem; opacity: 0.7; font-size: 0.9rem; margin-top: 0.25rem;">
                    <i class="fas fa-users" style="color: #3B82F6;"></i>
                    <span>Rejoint par: <strong style="color: #3B82F6;">${joinedBy.join(', ')}</strong></span>
                </div>
                ` : ''}
            </div>
            
            ${ticket.channel_id ? `
            <div style="font-size: 0.85rem; opacity: 0.7;">
                <i class="fas fa-hashtag"></i> Canal: ${ticket.channel_name || ticket.channel_id}
            </div>
            ` : ''}
        `;
        
        ticketsList.appendChild(ticketCard);
    });
    
    if (tickets.length > 50) {
        const moreText = document.createElement('p');
        moreText.style.cssText = 'text-align: center; opacity: 0.7; margin-top: 1rem; grid-column: 1 / -1;';
        moreText.textContent = `+${tickets.length - 50} autres tickets...`;
        ticketsList.appendChild(moreText);
    }
    
    container.appendChild(ticketsList);
}

function filterTickets() {
    if (!currentTicketsData || !currentTicketsData.tickets) return;
    
    const statusFilter = document.getElementById('ticketStatusFilter').value;
    const priorityFilter = document.getElementById('ticketPriorityFilter').value;
    
    let filteredTickets = currentTicketsData.tickets;
    
    if (statusFilter === 'open') {
        filteredTickets = filteredTickets.filter(t => t.status === 'open');
    } else if (statusFilter === 'closed') {
        filteredTickets = filteredTickets.filter(t => t.status === 'closed');
    }
    
    if (priorityFilter !== 'all') {
        filteredTickets = filteredTickets.filter(t => (t.priority || 'normal') === priorityFilter);
    }
    
    displayTickets(filteredTickets);
}



let currentWarnsData = null;

async function loadWarnsPage() {
    try {
        await loadWarnConfig();
        await loadWarnsStats();
        await loadWarns();
    } catch (error) {
        console.error('Erreur chargement warns:', error);
        showError('Impossible de charger les avertissements');
    }
}

async function loadWarnConfig() {
    try {
        const response = await fetch(addTokenToUrl(`/api/guilds/${currentGuildId}/warn-config`));
        const config = await response.json();
        
        displayWarnRules(config.actions || {});
    } catch (error) {
        console.error('Erreur chargement config warns:', error);
    }
}

function displayWarnRules(actions) {
    const container = document.getElementById('warnRulesList');
    container.innerHTML = '';
    
    if (Object.keys(actions).length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 2rem; opacity: 0.6; background: rgba(255,255,255,0.02); border-radius: 12px; border: 2px dashed rgba(255,255,255,0.1);">
                <i class="fas fa-info-circle" style="font-size: 2rem; margin-bottom: 0.5rem;"></i>
                <p>Aucune règle configurée. Cliquez sur "Ajouter une règle automatique" pour commencer.</p>
            </div>
        `;
        return;
    }
    
    const sortedKeys = Object.keys(actions).sort((a, b) => parseInt(a) - parseInt(b));
    
    const colors = [
        { bg: 'rgba(239, 68, 68, 0.05)', border: '#EF4444', icon: '#EF4444' },
        { bg: 'rgba(245, 158, 11, 0.05)', border: '#F59E0B', icon: '#F59E0B' },
        { bg: 'rgba(139, 92, 246, 0.05)', border: '#8B5CF6', icon: '#8B5CF6' },
        { bg: 'rgba(99, 102, 241, 0.05)', border: '#6366F1', icon: '#6366F1' },
        { bg: 'rgba(236, 72, 153, 0.05)', border: '#EC4899', icon: '#EC4899' },
        { bg: 'rgba(16, 185, 129, 0.05)', border: '#10B981', icon: '#10B981' },
    ];
    
    sortedKeys.forEach((warnCount, index) => {
        const action = actions[warnCount];
        const color = colors[index % colors.length];
        
        const actionIcon = action.type === 'timeout' ? '⏰' : action.type === 'kick' ? '👢' : '🔨';
        const actionName = action.type === 'timeout' ? 'Timeout' : action.type === 'kick' ? 'Kick' : 'Ban';
        
        const ruleDiv = document.createElement('div');
        ruleDiv.className = 'warn-rule';
        ruleDiv.style.cssText = `
            padding: 1.25rem; 
            background: ${color.bg}; 
            border-radius: 12px; 
            border-left: 4px solid ${color.border};
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        `;
        
        ruleDiv.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: start; gap: 1rem;">
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                        <div style="width: 40px; height: 40px; background: ${color.border}; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem;">
                            ${actionIcon}
                        </div>
                        <div>
                            <strong style="font-size: 1.1rem; display: block;">${warnCount} Avertissement(s)</strong>
                            <span style="opacity: 0.7; font-size: 0.9rem;">Action: ${actionName}</span>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-top: 0.75rem;">
                        <div>
                            <label style="display: block; margin-bottom: 0.5rem; opacity: 0.8; font-size: 0.9rem;">Nombre de warns</label>
                            <input type="number" id="warnCount_${warnCount}" class="form-control" value="${warnCount}" min="1" max="100" 
                                style="background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 0.5rem;">
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: 0.5rem; opacity: 0.8; font-size: 0.9rem;">Action</label>
                            <select id="warnAction_${warnCount}" class="form-control" onchange="toggleDurationField('${warnCount}')"
                                style="background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 0.5rem;">
                                <option value="timeout" ${action.type === 'timeout' ? 'selected' : ''}>⏰ Timeout</option>
                                <option value="kick" ${action.type === 'kick' ? 'selected' : ''}>👢 Kick</option>
                                <option value="ban" ${action.type === 'ban' ? 'selected' : ''}>🔨 Ban</option>
                            </select>
                        </div>
                        <div id="warnDuration_${warnCount}_container" style="${action.type === 'timeout' ? '' : 'display: none;'}">
                            <label style="display: block; margin-bottom: 0.5rem; opacity: 0.8; font-size: 0.9rem;">Durée (min)</label>
                            <input type="number" id="warnDuration_${warnCount}" class="form-control" value="${action.duration ? action.duration / 60 : 60}" min="1"
                                style="background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 0.5rem;">
                        </div>
                    </div>
                </div>
                <button onclick="removeWarnRule('${warnCount}')" class="btn btn-danger" 
                    style="padding: 0.5rem 0.75rem; border-radius: 8px; background: rgba(239, 68, 68, 0.2); border: 1px solid #EF4444; transition: all 0.2s;">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        
        container.appendChild(ruleDiv);
    });
}

function toggleDurationField(warnCount) {
    const action = document.getElementById(`warnAction_${warnCount}`).value;
    const durationContainer = document.getElementById(`warnDuration_${warnCount}_container`);
    
    if (action === 'timeout') {
        durationContainer.style.display = 'block';
    } else {
        durationContainer.style.display = 'none';
    }
}

function addWarnRule() {
    const container = document.getElementById('warnRulesList');
    const existingRules = container.querySelectorAll('.warn-rule');
    
    let newCount = 1;
    const usedCounts = [];
    
    existingRules.forEach(rule => {
        const input = rule.querySelector('input[type="number"]');
        if (input) {
            usedCounts.push(parseInt(input.value));
        }
    });
    
    while (usedCounts.includes(newCount)) {
        newCount++;
    }
    
    const newActions = {};
    
    existingRules.forEach(rule => {
        const countInput = rule.querySelector('input[type="number"]');
        if (countInput) {
            const count = countInput.value;
            const actionSelect = document.getElementById(`warnAction_${countInput.defaultValue || count}`);
            const durationInput = document.getElementById(`warnDuration_${countInput.defaultValue || count}`);
            
            newActions[count] = {
                type: actionSelect?.value || 'timeout',
                enabled: true,
                duration: durationInput ? parseInt(durationInput.value) * 60 : 3600
            };
        }
    });
    
    newActions[newCount] = {
        type: 'timeout',
        enabled: true,
        duration: 3600
    };
    
    displayWarnRules(newActions);
}

function removeWarnRule(warnCount) {
    if (!confirm(`Voulez-vous vraiment supprimer la règle pour ${warnCount} avertissement(s) ?`)) {
        return;
    }
    
    const container = document.getElementById('warnRulesList');
    const rules = container.querySelectorAll('.warn-rule');
    
    const newActions = {};
    
    rules.forEach(rule => {
        const countInput = rule.querySelector('input[type="number"]');
        if (countInput && countInput.value !== warnCount) {
            const count = countInput.value;
            const actionSelect = document.getElementById(`warnAction_${countInput.defaultValue || count}`);
            const durationInput = document.getElementById(`warnDuration_${countInput.defaultValue || count}`);
            
            newActions[count] = {
                type: actionSelect?.value || 'timeout',
                enabled: true,
                duration: durationInput ? parseInt(durationInput.value) * 60 : 3600
            };
        }
    });
    
    displayWarnRules(newActions);
}

async function saveWarnConfig() {
    const statusEl = document.getElementById('warnConfigStatus');
    statusEl.textContent = '💾 Sauvegarde en cours...';
    statusEl.style.color = '#F59E0B';
    
    try {
        const container = document.getElementById('warnRulesList');
        const rules = container.querySelectorAll('.warn-rule');
        
        const config = {
            actions: {},
            dm_enabled: true,
            log_channel: null
        };
        
        rules.forEach(rule => {
            const countInput = rule.querySelector('input[type="number"]');
            if (countInput) {
                const originalCount = countInput.defaultValue || countInput.value;
                const newCount = countInput.value;
                
                const actionSelect = document.getElementById(`warnAction_${originalCount}`);
                const durationInput = document.getElementById(`warnDuration_${originalCount}`);
                
                if (actionSelect) {
                    config.actions[String(newCount)] = {
                        type: actionSelect.value,
                        enabled: true
                    };
                    
                    if (actionSelect.value === 'timeout' && durationInput) {
                        config.actions[String(newCount)].duration = parseInt(durationInput.value) * 60;
                    }
                }
            }
        });
        
        const response = await fetch(addTokenToUrl(`/api/guilds/${currentGuildId}/warn-config`), {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        if (response.ok) {
            statusEl.textContent = '✅ Configuration sauvegardée avec succès !';
            statusEl.style.color = '#10B981';
            setTimeout(() => {
                statusEl.textContent = '';
            }, 3000);
            await loadWarnConfig();
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Erreur de sauvegarde');
        }
    } catch (error) {
        console.error('Erreur sauvegarde config:', error);
        statusEl.textContent = '❌ Erreur lors de la sauvegarde: ' + error.message;
        statusEl.style.color = '#EF4444';
    }
}

async function loadWarnsStats() {
    try {
        const response = await fetch(addTokenToUrl(`/api/guilds/${currentGuildId}/warns`));
        const data = await response.json();
        
        const warns = data.warns || {};
        const allWarns = [];
        
        Object.keys(warns).forEach(userId => {
            warns[userId].forEach(warn => {
                allWarns.push({
                    userId: userId,
                    ...warn
                });
            });
        });
        
        document.getElementById('totalWarns').textContent = allWarns.length;
        document.getElementById('totalWarnedUsers').textContent = Object.keys(warns).length;
        
        const today = new Date().toISOString().split('T')[0];
        const warnsToday = allWarns.filter(w => w.timestamp && w.timestamp.startsWith(today)).length;
        document.getElementById('warnsToday').textContent = warnsToday;
        
        if (Object.keys(warns).length > 0) {
            const mostWarned = Object.entries(warns).reduce((max, [userId, userWarns]) => 
                userWarns.length > (warns[max] || []).length ? userId : max
            );
            
            try {
                const membersResponse = await fetch(`/api/guilds/${currentGuildId}/members`);
                const members = await membersResponse.json();
                const member = members.find(m => m.id === mostWarned);
                if (member) {
                    document.getElementById('topWarned').textContent = member.username;
                } else {
                    document.getElementById('topWarned').textContent = mostWarned.slice(0, 8) + '...';
                }
            } catch {
                document.getElementById('topWarned').textContent = mostWarned.slice(0, 8) + '...';
            }
        } else {
            document.getElementById('topWarned').textContent = '-';
        }
    } catch (error) {
        console.error('Erreur stats warns:', error);
    }
}

async function loadWarns() {
    try {
        const response = await fetch(addTokenToUrl(`/api/guilds/${currentGuildId}/warns`));
        const data = await response.json();
        
        currentWarnsData = data;
        await displayWarns(data.warns || {});
    } catch (error) {
        console.error('Erreur chargement warns:', error);
        document.getElementById('warnsList').innerHTML = `
            <div style="text-align: center; padding: 2rem; color: #EF4444;">
                <i class="fas fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 1rem;"></i>
                <p>Erreur de chargement des avertissements</p>
            </div>
        `;
    }
}

async function displayWarns(warns) {
    const container = document.getElementById('warnsList');
    
    if (!warns || Object.keys(warns).length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 3rem; opacity: 0.7;">
                <i class="fas fa-check-circle" style="font-size: 3rem; color: #10B981; margin-bottom: 1rem;"></i>
                <h3>Aucun avertissement</h3>
                <p>Ce serveur n'a aucun membre averti</p>
            </div>
        `;
        return;
    }
    

    let members = [];
    try {
        const membersResponse = await fetch(`/api/guilds/${currentGuildId}/members`);
        members = await membersResponse.json();
    } catch (error) {
        console.error('Erreur récupération membres:', error);
    }
    
    container.innerHTML = '';
    const warnList = document.createElement('div');
    warnList.className = 'warn-list';
    warnList.style.display = 'grid';
    warnList.style.gridTemplateColumns = 'repeat(auto-fill, minmax(350px, 1fr))';
    warnList.style.gap = '1rem';
    
    const sortedWarns = Object.entries(warns).sort((a, b) => b[1].length - a[1].length);
    
    for (const [userId, userWarns] of sortedWarns) {
        const member = members.find(m => m.id === userId);
        const memberName = member ? member.username : `Utilisateur ${userId.slice(0, 8)}...`;
        const memberAvatar = member && member.avatar ? member.avatar : null;
        
        const warnItem = document.createElement('div');
        warnItem.className = 'warn-item';
        warnItem.style.padding = '1.25rem';
        warnItem.style.background = 'rgba(239, 68, 68, 0.1)';
        warnItem.style.border = '1px solid rgba(239, 68, 68, 0.3)';
        warnItem.style.borderRadius = '8px';
        warnItem.style.display = 'flex';
        warnItem.style.flexDirection = 'column';
        warnItem.style.gap = '1rem';
        
        const avatarUrl = memberAvatar || 'https://cdn.discordapp.com/embed/avatars/0.png';
        
        let warnsHtml = '';
        userWarns.forEach((warn, index) => {
            const warnDate = warn.timestamp ? new Date(warn.timestamp).toLocaleDateString('fr-FR') : 'Date inconnue';
            const moderator = warn.moderator_name || warn.moderator || 'Modérateur inconnu';
            
            warnsHtml += `
                <div style="padding: 0.75rem; background: rgba(0, 0, 0, 0.2); border-radius: 6px; margin-top: ${index > 0 ? '0.5rem' : '0'};">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                        <div style="font-size: 0.85rem; opacity: 0.7;">
                            <i class="fas fa-calendar"></i> ${warnDate}
                        </div>
                        <button class="btn btn-danger btn-sm" onclick="removeWarn('${userId}', ${warn.id || index})" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div contenteditable="true" 
                         id="warn_reason_${userId}_${warn.id || index}" 
                         style="background: rgba(0,0,0,0.2); padding: 0.5rem; border-radius: 4px; margin-bottom: 0.5rem; border: 1px solid rgba(255,255,255,0.05); min-height: 30px; outline: none; font-size: 0.9rem;"
                         onblur="updateWarnReason('${userId}', ${warn.id || index}, this.textContent)">
                        ${warn.reason || 'Aucune raison spécifiée'}
                    </div>
                    <div style="font-size: 0.85rem; opacity: 0.6;">
                        <i class="fas fa-user-shield"></i> Par: <strong>${moderator}</strong>
                    </div>
                </div>
            `;
        });
        
        warnItem.innerHTML = `
            <div style="display: flex; align-items: center; gap: 1rem; flex: 1;">
                <div style="width: 50px; height: 50px; border-radius: 50%; overflow: hidden; flex-shrink: 0; border: 2px solid rgba(239, 68, 68, 0.5);">
                    <img src="${avatarUrl}" alt="${memberName}" style="width: 100%; height: 100%; object-fit: cover;">
                </div>
                <div style="flex: 1; min-width: 0;">
                    <h4 style="margin: 0; font-size: 1.05rem; margin-bottom: 0.25rem;">${memberName}</h4>
                    <p style="margin: 0; font-size: 0.85rem; opacity: 0.7;">ID: ${userId}</p>
                    <div style="margin-top: 0.5rem;">
                        <span style="background: rgba(239, 68, 68, 0.3); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.85rem; font-weight: 600;">
                            <i class="fas fa-exclamation-triangle"></i> ${userWarns.length} warn${userWarns.length > 1 ? 's' : ''}
                        </span>
                    </div>
                </div>
            </div>
            <div>
                ${warnsHtml}
            </div>
            <button class="btn btn-danger" onclick="clearUserWarns('${userId}')" style="width: 100%; margin-top: 0.5rem;">
                <i class="fas fa-trash"></i> Supprimer tous les warns
            </button>
        `;
        warnList.appendChild(warnItem);
    }
    
    container.appendChild(warnList);
}

async function updateWarnReason(userId, warnId, newReason) {
    if (!newReason || newReason.trim() === '') {
        showError('La raison ne peut pas être vide');
        await loadWarns();
        return;
    }
    
    try {
        const response = await fetch(addTokenToUrl(`/api/guilds/${currentGuildId}/warns/${userId}/${warnId}`), {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                reason: newReason.trim()
            })
        });
        
        if (response.ok) {
            showSuccess('Raison du warn mise à jour');
            await loadWarns();
        } else {
            const error = await response.json();
            showError(error.error || 'Erreur lors de la mise à jour');
            await loadWarns();
        }
    } catch (error) {
        console.error('Erreur mise à jour warn:', error);
        showError('Impossible de mettre à jour le warn');
        await loadWarns();
    }
}

async function removeWarn(userId, warnId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cet avertissement ?')) return;
    
    try {
        const response = await fetch(addTokenToUrl(`/api/guilds/${currentGuildId}/warns/${userId}/${warnId}`), {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showSuccess('Avertissement supprimé avec succès');
            await loadWarns();
            await loadWarnsStats();
        } else {
            const error = await response.json();
            showError(error.error || 'Erreur lors de la suppression');
        }
    } catch (error) {
        console.error('Erreur suppression warn:', error);
        showError('Impossible de supprimer l\'avertissement');
    }
}

async function clearUserWarns(userId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer TOUS les avertissements de cet utilisateur ?')) return;
    
    try {
        const response = await fetch(addTokenToUrl(`/api/guilds/${currentGuildId}/warns?user_id=${userId}`), {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showSuccess('Tous les avertissements ont été supprimés');
            await loadWarns();
            await loadWarnsStats();
        } else {
            const error = await response.json();
            showError(error.error || 'Erreur lors de la suppression');
        }
    } catch (error) {
        console.error('Erreur suppression warns:', error);
        showError('Impossible de supprimer les avertissements');
    }
}

function filterWarns() {
    const searchTerm = document.getElementById('warnSearchUser').value.toLowerCase();
    const sortBy = document.getElementById('warnSort').value;
    
    if (!currentWarnsData || !currentWarnsData.warns) return;
    
    let warns = { ...currentWarnsData.warns };
    
    if (searchTerm) {
        const filtered = {};
        Object.entries(warns).forEach(([userId, userWarns]) => {
            if (userId.toLowerCase().includes(searchTerm)) {
                filtered[userId] = userWarns;
            }
        });
        warns = filtered;
    }
    
    const sorted = Object.entries(warns).sort((a, b) => {
        if (sortBy === 'recent') {
            const aLatest = Math.max(...a[1].map(w => w.timestamp ? new Date(w.timestamp).getTime() : 0));
            const bLatest = Math.max(...b[1].map(w => w.timestamp ? new Date(w.timestamp).getTime() : 0));
            return bLatest - aLatest;
        } else if (sortBy === 'oldest') {
            const aOldest = Math.min(...a[1].map(w => w.timestamp ? new Date(w.timestamp).getTime() : Infinity));
            const bOldest = Math.min(...b[1].map(w => w.timestamp ? new Date(w.timestamp).getTime() : Infinity));
            return aOldest - bOldest;
        } else if (sortBy === 'most') {
            return b[1].length - a[1].length;
        }
        return 0;
    });
    
    const sortedWarns = Object.fromEntries(sorted);
    displayWarns(sortedWarns);
}

async function refreshWarns() {
    await loadWarns();
    await loadWarnsStats();
    showSuccess('Avertissements actualisés');
}

async function addNewWarn() {
    const userIdInput = document.getElementById('newWarnUserId');
    const reasonInput = document.getElementById('newWarnReason');
    const statusElement = document.getElementById('addWarnStatus');
    
    const userId = userIdInput.value.trim();
    const reason = reasonInput.value.trim();
    
    if (!userId) {
        statusElement.style.display = 'block';
        statusElement.style.background = 'rgba(239, 68, 68, 0.1)';
        statusElement.style.border = '2px solid rgba(239, 68, 68, 0.3)';
        statusElement.innerHTML = '<i class="fas fa-exclamation-circle" style="margin-right: 0.5rem; color: #EF4444;"></i><span style="color: #EF4444;">Veuillez entrer l\'ID du membre</span>';
        setTimeout(() => statusElement.style.display = 'none', 3000);
        return;
    }
    
    if (!/^\d+$/.test(userId)) {
        statusElement.style.display = 'block';
        statusElement.style.background = 'rgba(239, 68, 68, 0.1)';
        statusElement.style.border = '2px solid rgba(239, 68, 68, 0.3)';
        statusElement.innerHTML = '<i class="fas fa-exclamation-circle" style="margin-right: 0.5rem; color: #EF4444;"></i><span style="color: #EF4444;">L\'ID doit contenir uniquement des chiffres</span>';
        setTimeout(() => statusElement.style.display = 'none', 3000);
        return;
    }
    
    if (!reason) {
        statusElement.style.display = 'block';
        statusElement.style.background = 'rgba(239, 68, 68, 0.1)';
        statusElement.style.border = '2px solid rgba(239, 68, 68, 0.3)';
        statusElement.innerHTML = '<i class="fas fa-exclamation-circle" style="margin-right: 0.5rem; color: #EF4444;"></i><span style="color: #EF4444;">Veuillez entrer une raison</span>';
        setTimeout(() => statusElement.style.display = 'none', 3000);
        return;
    }
    
    try {
        statusElement.style.display = 'block';
        statusElement.style.background = 'rgba(245, 158, 11, 0.1)';
        statusElement.style.border = '2px solid rgba(245, 158, 11, 0.3)';
        statusElement.innerHTML = '<i class="fas fa-spinner fa-spin" style="margin-right: 0.5rem; color: #F59E0B;"></i><span style="color: #F59E0B;">Ajout de l\'avertissement en cours...</span>';
        
        const discordUser = JSON.parse(localStorage.getItem('discord_user') || '{}');
        
        const response = await fetch(addTokenToUrl(`/api/guilds/${currentGuildId}/warns`), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: userId,
                reason: reason,
                moderator_id: discordUser.id || 'unknown',
                moderator_name: discordUser.username ? `${discordUser.username}#${discordUser.discriminator || '0000'}` : 'Panel Web'
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            let successMessage = '<i class="fas fa-check-circle" style="margin-right: 0.5rem; color: #10B981;"></i><span style="color: #10B981;">Avertissement ajouté avec succès!';
            
            if (result.action_taken) {
                successMessage += `<br><small style="color: #F59E0B;"><i class="fas fa-bolt"></i> Action automatique: ${result.action_taken}</small>`;
            }
            
            successMessage += '</span>';
            
            statusElement.style.background = 'rgba(16, 185, 129, 0.1)';
            statusElement.style.border = '2px solid rgba(16, 185, 129, 0.3)';
            statusElement.innerHTML = successMessage;
            
s
            reasonInput.value = '';
            userIdInput.value = '';
            

            await loadWarns();
            await loadWarnsStats();
            
            setTimeout(() => {
                statusElement.style.display = 'none';
            }, 5000);
        } else {
            const error = await response.json();
            statusElement.style.background = 'rgba(239, 68, 68, 0.1)';
            statusElement.style.border = '2px solid rgba(239, 68, 68, 0.3)';
            statusElement.innerHTML = `<i class="fas fa-times-circle" style="margin-right: 0.5rem; color: #EF4444;"></i><span style="color: #EF4444;">${error.error || 'Erreur lors de l\'ajout'}</span>`;
            setTimeout(() => statusElement.style.display = 'none', 4000);
        }
    } catch (error) {
        console.error('Erreur ajout warn:', error);
        statusElement.style.display = 'block';
        statusElement.style.background = 'rgba(239, 68, 68, 0.1)';
        statusElement.style.border = '2px solid rgba(239, 68, 68, 0.3)';
        statusElement.innerHTML = '<i class="fas fa-exclamation-triangle" style="margin-right: 0.5rem; color: #EF4444;"></i><span style="color: #EF4444;">Impossible d\'ajouter l\'avertissement</span>';
        setTimeout(() => statusElement.style.display = 'none', 4000);
    }
}

async function loadMembersForWarn() {

}
