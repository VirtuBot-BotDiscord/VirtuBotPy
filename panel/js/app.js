let currentGuilds = [];
let userGuilds = [];
let discordUser = null;
let ADMIN_USER_ID = null;

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Panel VirtuBot chargé');
    
    const token = localStorage.getItem('discord_token');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }
    
    try {
        await loadUserData();
        

        const adminResponse = await fetch('/api/admin/id');
        if (adminResponse.ok) {
            const adminData = await adminResponse.json();
            ADMIN_USER_ID = adminData.admin_id;
        }
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
            e.preventDefault();
            const page = item.getAttribute('data-page');
            navigateToPage(page);
            
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
            
            sidebar.classList.remove('active');
        });
    });

    await loadDashboard();
    

    console.log('🔍 Check updates - User ID:', discordUser?.id, 'Admin ID:', ADMIN_USER_ID);
    if (discordUser && ADMIN_USER_ID && String(discordUser.id) === String(ADMIN_USER_ID)) {
        console.log('✅ User is admin, checking for updates...');
        await checkForUpdates();
    } else {
        console.log('❌ User is not admin or ADMIN_USER_ID not set');
    }
    
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
    
    const guildsResponse = await fetch('https://discord.com/api/users/@me/guilds', {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!guildsResponse.ok) throw new Error('Failed to fetch guilds');
    userGuilds = await guildsResponse.json();
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
            case 'dashboard':
                loadDashboard();
                break;
            case 'guilds':
                loadGuilds();
                break;
            case 'commands':
                loadCommands();
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

async function loadDashboard() {
    try {

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
        
        const stats = await getBotStats();
        
        const botGuilds = await getGuilds();
        const adminGuilds = botGuilds.filter(botGuild => {
            const userGuild = userGuilds.find(ug => ug.id === botGuild.id);
            if (!userGuild) return false;
            const hasAdmin = (userGuild.permissions & 0x8) === 0x8;
            return hasAdmin;
        });
        
        document.getElementById('adminGuildCount').textContent = adminGuilds.length;
        document.getElementById('latency').textContent = stats.latency;
        
        try {
            const commands = await getBotCommands();
            document.getElementById('commandCount').textContent = commands.length;
        } catch (error) {
            document.getElementById('commandCount').textContent = '?';
        }
        
        await checkBotStatus();
    } catch (error) {
        console.error('Erreur lors du chargement du dashboard:', error);

        document.getElementById('adminGuildCount').textContent = '0';
        document.getElementById('latency').textContent = '?';
        document.getElementById('commandCount').textContent = '?';
        

        const dashboardPage = document.getElementById('dashboard-page');
        if (dashboardPage && !document.querySelector('.error-banner')) {
            const errorBanner = document.createElement('div');
            errorBanner.className = 'error-banner';
            errorBanner.style.cssText = 'background: #ED4245; color: white; padding: 1rem; border-radius: 8px; margin-top: 1rem; text-align: center; display: flex; align-items: center; justify-content: center; gap: 0.5rem;';
            errorBanner.innerHTML = `
                <i class="fas fa-exclamation-triangle"></i> 
                <span>Impossible de charger les statistiques du bot. Vérifiez que le bot est en ligne.</span>
                <button onclick="location.reload()" style="margin-left: 1rem; background: white; color: #ED4245; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer; font-weight: bold;">
                    <i class="fas fa-sync"></i> Réessayer
                </button>
            `;
            const statsGrid = dashboardPage.querySelector('.stats-grid');
            if (statsGrid) {
                statsGrid.parentElement.insertBefore(errorBanner, statsGrid.nextSibling);
            }
        }
    }
}

async function loadGuilds() {
    const guildsList = document.getElementById('guildsList');
    guildsList.innerHTML = '<p class="loading">Chargement des serveurs...</p>';
    
    try {
        const guilds = await getGuilds();
        

        const adminGuilds = guilds.filter(guild => {
            const userGuild = userGuilds.find(ug => ug.id === guild.id);
            if (!userGuild) return false;
            const hasAdmin = (userGuild.permissions & 0x8) === 0x8;
            return hasAdmin;
        });
        
        currentGuilds = adminGuilds;
        
        if (adminGuilds.length === 0) {
            guildsList.innerHTML = '<p class="loading">Aucun serveur trouvé où vous êtes administrateur</p>';
            return;
        }
        
        guildsList.innerHTML = '';
        adminGuilds.forEach(guild => {
            const guildCard = document.createElement('div');
            guildCard.className = 'guild-card';
            guildCard.onclick = () => {

                window.location.href = `serveur.html?guild=${guild.id}`;
            };
            

            const userGuild = userGuilds.find(ug => ug.id === guild.id);
            const isOwner = userGuild && userGuild.owner === true;
            
            guildCard.innerHTML = `
                <div class="guild-icon">
                    ${guild.icon ? `<img src="${guild.icon}" alt="${guild.name}">` : guild.name.charAt(0)}
                </div>
                <div class="guild-info">
                    <h3>
                        ${guild.name}
                        ${isOwner ? '<span style="margin-left: 0.5rem;" title="Propriétaire du serveur">👑</span>' : ''}
                    </h3>
                    <p><i class="fas fa-users"></i> ${guild.memberCount} membres</p>
                </div>
            `;
            guildsList.appendChild(guildCard);
        });
    } catch (error) {
        console.error('Erreur lors du chargement des serveurs:', error);
        guildsList.innerHTML = '<p class="loading">Erreur lors du chargement des serveurs</p>';
    }
}

async function loadCommands() {
    const commandsList = document.getElementById('commandsList');
    commandsList.innerHTML = '<p class="loading">Chargement des commandes...</p>';
    
    try {
        const commands = await getBotCommands();
        
        if (commands.length === 0) {
            commandsList.innerHTML = '<p class="loading">Aucune commande trouvée</p>';
            return;
        }
        

        const categories = {};
        commands.forEach(cmd => {
            const category = cmd.category || 'Autres';
            if (!categories[category]) {
                categories[category] = [];
            }
            categories[category].push(cmd);
        });
        

        const categoryConfig = {
            'Base': {
                icon: '📚',
                color: '#6366F1',
                gradient: 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)',
                description: 'Commandes essentielles du bot'
            },
            'Administration': {
                icon: '🛡️',
                color: '#F59E0B',
                gradient: 'linear-gradient(135deg, #F59E0B 0%, #EF4444 100%)',
                description: 'Gestion et modération du serveur'
            },
            'Jeux': {
                icon: '🎮',
                color: '#10B981',
                gradient: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
                description: 'Mini-jeux et divertissement'
            },
            'Utilitaires': {
                icon: '🔧',
                color: '#3B82F6',
                gradient: 'linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)',
                description: 'Outils et utilitaires serveur'
            },
            'Tickets': {
                icon: '🎫',
                color: '#8B5CF6',
                gradient: 'linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%)',
                description: 'Système de support client'
            },
            'Panel': {
                icon: '🌐',
                color: '#06B6D4',
                gradient: 'linear-gradient(135deg, #06B6D4 0%, #0891B2 100%)',
                description: 'Interface web et API'
            },
            'Autres': {
                icon: '📦',
                color: '#6B7280',
                gradient: 'linear-gradient(135deg, #6B7280 0%, #4B5563 100%)',
                description: 'Commandes diverses'
            }
        };
        
        commandsList.innerHTML = '';
        

        const categoryOrder = ['Base', 'Administration', 'Jeux', 'Utilitaires', 'Tickets', 'Panel', 'Autres'];
        const sortedCategories = categoryOrder.filter(cat => categories[cat]);
        Object.keys(categories).forEach(cat => {
            if (!sortedCategories.includes(cat)) {
                sortedCategories.push(cat);
            }
        });
        
        sortedCategories.forEach(category => {
            if (!categories[category]) return;
            
            const categoryDiv = document.createElement('div');
            categoryDiv.className = 'command-category';
            categoryDiv.style.marginBottom = '2.5rem';
            
            const config = categoryConfig[category] || categoryConfig['Autres'];
            

            const categoryHeader = document.createElement('div');
            categoryHeader.className = 'category-header-styled';
            categoryHeader.style.cssText = `
                position: relative;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
                background: ${config.gradient};
                border-radius: 12px;
                box-shadow: 0 4px 16px ${config.color}40;
                overflow: hidden;
            `;
        
            const decorativeBorder = document.createElement('div');
            decorativeBorder.style.cssText = `
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: 
                    linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px),
                    linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px);
                background-size: 20px 20px;
                opacity: 0.1;
                pointer-events: none;
            `;
            categoryHeader.appendChild(decorativeBorder);
            
            const headerContent = document.createElement('div');
            headerContent.style.cssText = `
                position: relative;
                display: flex;
                align-items: center;
                gap: 1rem;
            `;
            headerContent.innerHTML = `
                <div style="font-size: 2.5rem; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));">${config.icon}</div>
                <div style="flex: 1;">
                    <h3 style="margin: 0; font-size: 1.5rem; color: white; text-shadow: 0 2px 4px rgba(0,0,0,0.3); font-weight: 700;">
                        ${category}
                    </h3>
                    <p style="margin: 0.25rem 0 0 0; color: rgba(255,255,255,0.9); font-size: 0.9rem; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">
                        ${config.description}
                    </p>
                </div>
                <div style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; backdrop-filter: blur(10px);">
                    <span style="color: white; font-weight: 600; font-size: 0.95rem;">${categories[category].length} commande${categories[category].length > 1 ? 's' : ''}</span>
                </div>
            `;
            categoryHeader.appendChild(headerContent);
            categoryDiv.appendChild(categoryHeader);
            
            const commandsGrid = document.createElement('div');
            commandsGrid.style.cssText = `
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                gap: 1rem;
            `;
            
            categories[category].forEach(cmd => {
                const commandItem = document.createElement('div');
                commandItem.className = 'command-item';
                commandItem.style.cssText = `
                    background: var(--card-bg);
                    padding: 1.25rem;
                    border-radius: 10px;
                    border: 2px solid var(--border-color);
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    cursor: pointer;
                    position: relative;
                    overflow: hidden;
                    background: linear-gradient(135deg, var(--card-bg) 0%, rgba(${parseInt(config.color.slice(1,3), 16)}, ${parseInt(config.color.slice(3,5), 16)}, ${parseInt(config.color.slice(5,7), 16)}, 0.05) 100%);
                `;
                
                commandItem.innerHTML = `
                    <div style="position: absolute; top: 0; left: 0; right: 0; height: 4px; background: ${config.gradient};"></div>
                    <div style="display: flex; align-items: start; justify-content: space-between; margin-bottom: 0.75rem;">
                        <span class="command-name" style="font-weight: 700; color: ${config.color}; font-size: 1.15rem; display: flex; align-items: center; gap: 0.5rem;">
                            <span style="opacity: 0.6;">/</span>${cmd.name}
                        </span>
                        <div style="background: ${config.color}20; padding: 0.25rem 0.5rem; border-radius: 6px;">
                            <i class="fas fa-terminal" style="color: ${config.color}; font-size: 0.9rem;"></i>
                        </div>
                    </div>
                    <p class="command-description" style="margin: 0; color: var(--text-secondary); font-size: 0.95rem; line-height: 1.6;">
                        ${cmd.description || 'Aucune description disponible'}
                    </p>
                `;
                

                commandItem.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-5px) scale(1.02)';
                    this.style.boxShadow = `0 12px 28px ${config.color}50, 0 0 0 1px ${config.color}`;
                    this.style.borderColor = config.color;
                });
                
                commandItem.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0) scale(1)';
                    this.style.boxShadow = 'none';
                    this.style.borderColor = 'var(--border-color)';
                });
                
                commandsGrid.appendChild(commandItem);
            });
            
            categoryDiv.appendChild(commandsGrid);
            commandsList.appendChild(categoryDiv);
        });
    } catch (error) {
        console.error('Erreur lors du chargement des commandes:', error);
        commandsList.innerHTML = '<p class="loading">Erreur lors du chargement des commandes</p>';
    }
}

function saveApiUrl() {
    const apiUrl = document.getElementById('apiUrl').value;
    localStorage.setItem('apiUrl', apiUrl);
    showSuccess('URL de l\'API sauvegardée');
    setTimeout(() => {
        window.location.reload();
    }, 1000);
}

function showSuccess(message) {
    alert('✅ ' + message);
}

function showError(message) {
    alert('❌ ' + message);
}

async function showUserProfile() {
    if (!discordUser) return;
    

    let isAdmin = false;
    try {
        const adminCheck = await fetch('/api/admin/check', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: discordUser.id })
        });
        const adminData = await adminCheck.json();
        isAdmin = adminData.is_admin;
    } catch (error) {
        console.error('Erreur vérification admin:', error);
    }
    
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
    
    const adminButton = isAdmin ? `
        <a href="admin.html" class="btn" style="
            text-decoration: none; 
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem 1.5rem;
            background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%);
            color: white;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
            border: 2px solid #DC2626;
        " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 16px rgba(220, 38, 38, 0.4)';" 
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
            <i class="fas fa-crown"></i> Panel Administrateur
        </a>
    ` : '';
    
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
            ${isAdmin ? '<div style="position: absolute; top: 10px; left: 10px; background: linear-gradient(135deg, #DC2626, #991B1B); color: white; padding: 0.5rem 1rem; border-radius: 8px; font-size: 0.9rem; font-weight: 600;"><i class="fas fa-crown"></i> Admin</div>' : ''}
            <img src="${avatarUrl}" alt="Avatar" style="
                width: 200px;
                height: 200px;
                border-radius: 50%;
                margin-bottom: 1rem;
                border: 4px solid ${isAdmin ? '#DC2626' : 'var(--primary-color)'};
                ${isAdmin ? 'box-shadow: 0 0 20px rgba(220, 38, 38, 0.5);' : ''}
            ">
            <h2 style="color: ${isAdmin ? '#DC2626' : 'var(--primary-color)'}; margin-bottom: 0.5rem;">${discordUser.username}</h2>
            <p style="color: var(--text-secondary); margin-bottom: 1rem;">ID: ${discordUser.id}</p>
            <p style="color: var(--text-secondary); margin-bottom: 1rem;">
                <i class="fas fa-calendar-alt"></i> Compte créé le: ${new Date(parseInt(discordUser.id) / 4194304 + 1420070400000).toLocaleDateString('fr-FR', { year: 'numeric', month: 'long', day: 'numeric' })}
            </p>
            <div style="margin-top: 1.5rem; display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
                ${adminButton}
                <a href="https://discord.com/users/${discordUser.id}" target="_blank" class="btn btn-primary" style="text-decoration: none; display: inline-flex; align-items: center; gap: 0.5rem;">
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

async function checkForUpdates() {
    try {
        const response = await fetch('/api/update/check');
        const data = await response.json();
        
        if (data.update_available && data.update_info) {
            const updateInfo = data.update_info;
            
            if (updateInfo.type === 'modified_version') {
                const notification = document.createElement('div');
                notification.id = 'update-notification';
                notification.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
                    color: white;
                    padding: 1.5rem;
                    border-radius: 12px;
                    box-shadow: 0 8px 24px rgba(245, 158, 11, 0.4);
                    z-index: 10000;
                    max-width: 450px;
                    animation: slideIn 0.5s ease;
                `;
                
                notification.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                        <h3 style="margin: 0; display: flex; align-items: center; gap: 0.5rem;">
                            <i class="fas fa-exclamation-triangle"></i> Version non officielle
                        </h3>
                        <button onclick="this.closest('#update-notification').remove()" style="background: rgba(255,255,255,0.2); border: none; color: white; width: 24px; height: 24px; border-radius: 50%; cursor: pointer;">×</button>
                    </div>
                    <p style="margin: 0 0 0.5rem 0; font-weight: 600;">Version actuelle : ${updateInfo.current_version}</p>
                    <p style="margin: 0 0 0.5rem 0;">Dernière release : ${updateInfo.version}</p>
                    <p style="margin: 0 0 1rem 0; opacity: 0.9; font-size: 0.9rem; line-height: 1.5;">
                        ⚠️ Vous avez modifié <code>version.txt</code><br>
                        ❌ Vous ne serez plus averti des mises à jour<br>
                        💡 Version de développement ou non officielle
                    </p>
                    <div style="display: flex; gap: 0.75rem;">
                        <a href="${updateInfo.url}" target="_blank" class="btn" style="
                            background: white;
                            color: #F59E0B;
                            text-decoration: none;
                            padding: 0.5rem 1rem;
                            border-radius: 6px;
                            font-weight: 600;
                            display: inline-flex;
                            align-items: center;
                            gap: 0.5rem;
                        ">
                            <i class="fas fa-external-link-alt"></i> Voir les releases
                        </a>
                    </div>
                `;
                
                document.body.appendChild(notification);
                
            } else {
                const notification = document.createElement('div');
                notification.id = 'update-notification';
                notification.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: linear-gradient(135deg, #10B981 0%, #059669 100%);
                    color: white;
                    padding: 1.5rem;
                    border-radius: 12px;
                    box-shadow: 0 8px 24px rgba(16, 185, 129, 0.4);
                    z-index: 10000;
                    max-width: 400px;
                    animation: slideIn 0.5s ease;
                `;
                
                notification.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                        <h3 style="margin: 0; display: flex; align-items: center; gap: 0.5rem;">
                            <i class="fas fa-download"></i> Mise à jour disponible !
                        </h3>
                        <button onclick="this.closest('#update-notification').remove()" style="background: rgba(255,255,255,0.2); border: none; color: white; width: 24px; height: 24px; border-radius: 50%; cursor: pointer;">×</button>
                    </div>
                    <p style="margin: 0 0 0.5rem 0; font-weight: 600;">${updateInfo.name}</p>
                    <p style="margin: 0 0 1rem 0; opacity: 0.9; font-size: 0.9rem;">Version ${updateInfo.version}</p>
                    <div style="display: flex; gap: 0.75rem;">
                        <a href="${updateInfo.url}" target="_blank" class="btn" style="
                            background: white;
                            color: #10B981;
                            text-decoration: none;
                            padding: 0.5rem 1rem;
                            border-radius: 6px;
                            font-weight: 600;
                            display: inline-flex;
                            align-items: center;
                            gap: 0.5rem;
                        ">
                            <i class="fas fa-external-link-alt"></i> Voir les détails
                        </a>
                        <a href="${updateInfo.download_url}" target="_blank" class="btn" style="
                            background: rgba(255,255,255,0.2);
                            color: white;
                            text-decoration: none;
                            padding: 0.5rem 1rem;
                            border-radius: 6px;
                            font-weight: 600;
                            display: inline-flex;
                            align-items: center;
                            gap: 0.5rem;
                        ">
                            <i class="fas fa-download"></i> Télécharger
                        </a>
                    </div>
                `;
                
                document.body.appendChild(notification);
            }
            
            const style = document.createElement('style');
            style.textContent = `
                @keyframes slideIn {
                    from {
                        transform: translateX(120%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    } catch (error) {
        console.error('Erreur lors de la vérification des mises à jour:', error);
    }
}
