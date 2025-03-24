import scrapy
from urllib.parse import urljoin

class CoversSpider(scrapy.Spider):
    name = "covers"
    allowed_domains = ["covers.com"]
    start_urls = ["https://www.covers.com/sport/basketball/nba/teams"]

    seasons = {
        "2024-25": "",
        "2023-24": "/2023-2024",
        "2022-23": "/2022-2023",
        "2021-22": "/2021-2022",
        "2020-21": "/2020-2021",
        "2019-20": "/2019-2020",
    }

    def parse(self, response):
        # Extract all team page URLs
        team_links = response.css('a[href^="/sport/basketball/nba/teams/main/"]::attr(href)').getall()

        for link in team_links:
            for season, season_path in self.seasons.items():
                season_url = response.urljoin(link + season_path)  
                yield scrapy.Request(season_url, callback=self.parse_team, meta={"season": season})

    def parse_team(self, response):
        team_name = response.css("h1.covers-CoversMatchups-teamPagesH1 b::text").get().strip()
        season = response.meta["season"]

        past_games_table = response.css("div#past-results table.covers-CoversResults-Table")

        rows = past_games_table.css("tbody tr")

        for row in rows:
            date = row.css("td:nth-child(1)::text").get()
            if date:
                date = date.strip()

                yield {
                    "team": team_name,
                    "season": season,  
                    "date": date, 
                    "matchup": row.css("td:nth-child(2) a::text").get().strip(),
                    "final_score": row.css("td:nth-child(3) a::text").get().strip(),
                    "spread_outcome": row.css("td:nth-child(4) span::text").get(default="").strip(),
                    "closing_spread": row.css("td:nth-child(4)::text").getall()[-1].strip(),
                    "total_outcome": row.css("td:nth-child(5) span::text").get(default="").strip(),
                    "closing_total": row.css("td:nth-child(5)::text").getall()[-1].strip(),
                }