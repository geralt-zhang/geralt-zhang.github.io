class VisitAnalytics {
    constructor() {
        this.storageKey = 'site_analytics';
        this.init();
    }

    init() {
        this.recordVisit();
        this.displayStats();
    }

    getAnalytics() {
        const stored = localStorage.getItem(this.storageKey);
        return stored ? JSON.parse(stored) : {
            totalVisits: 0,
            pageVisits: {}
        };
    }

    saveAnalytics(data) {
        localStorage.setItem(this.storageKey, JSON.stringify(data));
    }

    recordVisit() {
        const analytics = this.getAnalytics();
        const now = new Date();
        const pagePath = window.location.pathname;
        const pageTitle = document.title;
        
        analytics.totalVisits++;
        
        if (!analytics.pageVisits[pagePath]) {
            analytics.pageVisits[pagePath] = {
                count: 0,
                title: pageTitle
            };
        }
        analytics.pageVisits[pagePath].count++;
        
        this.saveAnalytics(analytics);
    }

    // 显示页面访问统计
    displayStats() {
        const stats = this.getAnalytics();
        const statsDiv = document.createElement('div');
        statsDiv.id = 'visit-stats';
        
        const currentPage = window.location.pathname;
        const pageVisits = stats.pageVisits[currentPage]?.count || 0;
        const totalPages = Object.keys(stats.pageVisits).length;
        
        statsDiv.innerHTML = `
            <div>[TOTAL: ${stats.totalVisits}]</div>
            <div>[PAGE: ${pageVisits}]</div>
            <div style="opacity: 0.7; margin-top: 3px;">[PAGES: ${totalPages}]</div>
        `;
        
        document.body.appendChild(statsDiv);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.visitAnalytics = new VisitAnalytics();
});
