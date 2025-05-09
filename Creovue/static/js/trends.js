document.addEventListener("DOMContentLoaded", function () {
    const regionSelect = document.getElementById("region-select");
    const categorySelect = document.getElementById("category-select");
    const keywordSearch = document.getElementById("keyword-search");
    const refreshBtn = document.getElementById("refresh-data");

    async function fetchAndUpdateData() {
        const region = regionSelect.value;
        const category = categorySelect.value;
        const response = await fetch(`/api/trend_data?region=${region}&category=${category}`);
        const data = await response.json();

        updateKeywords(data.trending_keywords);
        updateCategoryDistribution(data.category_distribution);
        updateTopChannels(data.top_channels);

        document.getElementById("keywords-age").innerText = `Updated ${data.keyword_age}`;
        document.getElementById("category-age").innerText = `Updated ${data.category_age}`;
        document.getElementById("channels-age").innerText = `Updated ${data.channel_age}`;
    }

    function updateKeywords(keywords) {
        const container = document.getElementById("keywords-container");
        container.innerHTML = "";
        keywords.forEach(kw => {
            const span = document.createElement("span");
            span.className = "keyword-badge bg-primary text-white";
            span.innerText = kw.name;
            container.appendChild(span);
        });
    }

    function updateCategoryDistribution(distribution) {
        const list = document.querySelector(".trend-card:nth-child(2) .list-group");
        list.innerHTML = "";
        for (const [category, score] of Object.entries(distribution)) {
            const item = document.createElement("li");
            item.className = "list-group-item d-flex justify-content-between align-items-center";
            item.innerHTML = `${category}<span class="badge bg-success">${score}</span>`;
            list.appendChild(item);
        }
    }

    function updateTopChannels(channels) {
        const list = document.querySelector(".trend-card:nth-child(3) .list-group");
        list.innerHTML = "";
        channels.forEach(channel => {
            const item = document.createElement("li");
            item.className = "list-group-item d-flex align-items-center";
            item.innerHTML = `
                <img src="${channel.avatar_url}" alt="${channel.name}" class="channel-avatar me-3">
                <div>
                    <div><strong>${channel.name}</strong></div>
                    <div class="text-muted small">${channel.subscribers} subscribers</div>
                </div>`;
            list.appendChild(item);
        });
    }

    // Event Listeners
    regionSelect.addEventListener("change", fetchAndUpdateData);
    categorySelect.addEventListener("change", fetchAndUpdateData);
    refreshBtn.addEventListener("click", fetchAndUpdateData);

    // Initial fetch
    fetchAndUpdateData();
});
