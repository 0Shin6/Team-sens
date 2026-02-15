use axum::{extract::State, http::StatusCode, routing::{get, post}, Json, Router};
use reqwest::Client;
use serde::{Deserialize, Serialize};
use sqlx::{sqlite::SqlitePoolOptions, FromRow, SqlitePool};
use std::net::SocketAddr;
use tower_http::cors::CorsLayer;
use std::env;

#[derive(Clone)]
struct AppState {
    pool: SqlitePool,
    token_discord: Option<String>,
    discord_recip: Vec<String>,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    dotenv::dotenv().ok();
    let database_url = "sqlite://teamsens.db";
    let pool = SqlitePoolOptions::new().max_connections(5).connect(database_url).await.expect("Impossible de se connecter à la base de données. Vérifiez que le fichier existe.");
    let cors = CorsLayer::permissive();
    let token_discord = env::var("token_discord").ok().filter(|t| !t.trim().is_empty());
    let discord_recip = env::var("discord_recip").unwrap_or_default().split(',').map(|id| id.trim().to_string()).filter(|id| !id.is_empty()).collect::<Vec<_>>();
    
    let state = AppState {
        pool,
        token_discord,
        discord_recip,
    };

    let app = Router::new().route("/api/news", get(get_news)).route("/api/matches", get(get_matches)).route("/api/contact", post(post_contact)).layer(cors).with_state(state);
    let addr = SocketAddr::from(([127, 0, 0, 1], 3000));
    
    println!(" Serveur lancé sur http://{}", addr);
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

async fn get_news(State(state): State<AppState>) -> Json<Vec<NewsItem>> {
    let news = sqlx::query_as::<_, NewsItem>("SELECT id, titre, image, description FROM news ORDER BY id DESC LIMIT 5").fetch_all(&state.pool).await.unwrap_or_else(|_| vec![]);
    Json(news)
}

async fn get_matches(State(state): State<AppState>) -> Json<Vec<MatchItem>> {
    let matches = sqlx::query_as::<_, MatchItem>("SELECT id, team_a, team_b, score, date_heure, jeu FROM matches ORDER BY id DESC LIMIT 5").fetch_all(&state.pool).await.unwrap_or_else(|_| vec![]);
    Json(matches)
}

#[derive(Deserialize)]
struct ContactPayload {
    email: String,
    nom: String,
    discord: Option<String>,
    objet: String,
    message: String,
}

#[derive(Serialize)]
struct ContactResponse {
    ok: bool,
    erreur_recip: Vec<String>,
    message: String,
}

async fn post_contact(State(state): State<AppState>, Json(payload): Json<ContactPayload>) -> (StatusCode, Json<ContactResponse>) {
    if state.token_discord.is_none() || state.discord_recip.is_empty() {
        return (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(ContactResponse {
                ok: false,
                erreur_recip: vec![],
                message: "Discord n'est pas configuré sur le serveur.".to_string(),
            }),
        );
    }

    if payload.email.trim().is_empty() || payload.nom.trim().is_empty() || payload.objet.trim().is_empty() || payload.message.trim().is_empty() {
        return (
            StatusCode::BAD_REQUEST,
            Json(ContactResponse {
                ok: false,
                erreur_recip: vec![],
                message: "Champs obligatoires manquants.".to_string(),
            }),
        );
    }

    let discord_name = payload.discord.clone().unwrap_or_else(|| "Non renseigné".to_string());
    let contenu = format!(
        "Nouveau message via le formulaire de contact\n\nEmail: {}\nNom: {}\nDiscord: {}\nObjet: {}\n\nMessage:\n{}",
        payload.email.trim(),
        payload.nom.trim(),
        discord_name.trim(),
        payload.objet.trim(),
        payload.message.trim()
    );

    let token = state.token_discord.clone().unwrap();
    let client = Client::new();
    let mut failed = Vec::new();

    for id_recip in &state.discord_recip {
        if let Err(err) = send_dm(&client, &token, id_recip, &contenu).await {
            eprintln!("Erreur envoi DM à {}: {}", id_recip, err);
            failed.push(id_recip.clone());
        }
    }

    let ok = failed.is_empty();
    let status = if ok { StatusCode::OK } else { StatusCode::BAD_GATEWAY };

    (
        status,
        Json(ContactResponse {
            ok,
            erreur_recip: failed,
            message: if ok { 
                "Message envoyé.".to_string() } else { 
                "Message envoyé partiellement.".to_string() },
        }),
    )
}

async fn send_dm(client: &Client, token: &str, id_recip: &str, contenu: &str) -> Result<(), String> {
    let dm_resp = client
        .post("https://discord.com/api/v10/users/@me/channels")
        .header("Authorization", format!("Bot {}", token))
        .json(&serde_json::json!({ "recipient_id": id_recip }))
        .send()
        .await
        .map_err(|e| e.to_string())?;

    if !dm_resp.status().is_success() {
        let status = dm_resp.status();
        let body = dm_resp.text().await.unwrap_or_default();
        return Err(format!("Création DM échouée: {} - {}", status, body));
    }

    let dm_json: serde_json::Value = dm_resp.json().await.map_err(|e| e.to_string())?;
    let channel_id = dm_json.get("id").and_then(|v| v.as_str()).ok_or_else(|| "ID de salon DM manquant".to_string())?;
    let msg_resp = client
        .post(format!("https://discord.com/api/v10/channels/{}/messages", channel_id))
        .header("Authorization", format!("Bot {}", token))
        .json(&serde_json::json!({ "content": contenu }))
        .send()
        .await
        .map_err(|e| e.to_string())?;

    if !msg_resp.status().is_success() {
        let status = msg_resp.status();
        let body = msg_resp.text().await.unwrap_or_default();
        return Err(format!("Envoi DM échoué: {} - {}", status, body));
    }

    Ok(())
}