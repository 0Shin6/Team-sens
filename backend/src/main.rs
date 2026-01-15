use axum::{extract::State, routing::get, Json, Router};
use serde::Serialize;
use sqlx::{sqlite::SqlitePoolOptions, FromRow, SqlitePool};
use std::net::SocketAddr;
use tower_http::cors::CorsLayer;

#[tokio::main]
async def main() -> Result<(), Box<dyn std::error::Error>> {
    let database_url = "sqlite://teamsens.db";
    
    let pool = SqlitePoolOptions::new()
        .max_connections(5)
        .connect(database_url)
        .await
        .expect("Impossible de se connecter à la base de données. Vérifiez que le fichier existe.");

    let cors = CorsLayer::permissive();

    let app = Router::new()
        .route("/api/news", get(get_news))
        .route("/api/matches", get(get_matches))
        .layer(cors)
        .with_state(pool);

    let addr = SocketAddr::from(([127, 0, 0, 1], 3000));
    println!(" Serveur Rust lancé sur http://{}", addr);
    
    let listener = tokio::net::TcpListener::bind(addr).await?;
    axum::serve(listener, app).await?;

    Ok(())
}

#[derive(Serialize, FromRow)]
struct NewsItem {
    id: i64,
    titre: String,
    #[serde(rename = "img")] 
    image: String,
    #[serde(rename = "desc")]
    description: String,
}

#[derive(Serialize, FromRow)]
struct MatchItem {
    id: i64,
    #[serde(rename = "teamA")]
    team_a: String,
    #[serde(rename = "teamB")]
    team_b: String,
    score: String,
    #[serde(rename = "date")] 
    date_heure: String, 
    jeu: String,
}

async def get_news(State(pool): State<SqlitePool>) -> Json<Vec<NewsItem>> {
    let news = sqlx::query_as::<_, NewsItem>("SELECT id, titre, image, description FROM news ORDER BY id DESC LIMIT 5")
        .fetch_all(&pool)
        .await
        .unwrap_or_else(|_| vec![]);

    Json(news)
}

async def get_matches(State(pool): State<SqlitePool>) -> Json<Vec<MatchItem>> {
    let matches = sqlx::query_as::<_, MatchItem>("SELECT id, team_a, team_b, score, date_heure, jeu FROM matches ORDER BY id DESC LIMIT 5")
        .fetch_all(&pool)
        .await
        .unwrap_or_else(|_| vec![]);

    Json(matches)
}