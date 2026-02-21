-- Événements Valais V3 pour MapEventAI
-- Généré le 2026-02-06 22:27:06
-- 8 événements

-- Pour importer, utilisez l'API /api/events/scraped/batch
-- ou exécutez directement ce SQL

-- Ajouter les colonnes si elles n'existent pas
ALTER TABLE events ADD COLUMN IF NOT EXISTS source_url TEXT;
ALTER TABLE events ADD COLUMN IF NOT EXISTS organizer_name VARCHAR(255);
ALTER TABLE events ADD COLUMN IF NOT EXISTS organizer_email VARCHAR(255);
ALTER TABLE events ADD COLUMN IF NOT EXISTS validation_status VARCHAR(50) DEFAULT 'pending';
ALTER TABLE events ADD COLUMN IF NOT EXISTS validation_token VARCHAR(255);
ALTER TABLE events ADD COLUMN IF NOT EXISTS scraped_at TIMESTAMP;

-- Créer l'utilisateur système scraper
INSERT INTO users (id, email, username) VALUES ('system_scraper', 'scraper@mapevent.world', 'MapEvent Scraper') ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, end_date, categories, source_url, organizer_name, validation_status, status, creator_id, scraped_at)
VALUES (
    'Saison musicale 25/26',
    'Valais accueille cet événement. ConcertVe 06.02. -  Sa 30.05.2026Saison musicale 25/26Fondation Pierre Gianadda, MartignyEn savoir plusEn savoir plus',
    'Valais, Suisse',
    46.23628800739317,
    7.364154382976567,
    '2026-05-30',
    '2026-05-30',
    '["Music > Pop / Vari\u00e9t\u00e9", "Culture > Expositions"]'::jsonb,
    'https://agenda.culturevalais.ch/fr/event/show/38842',
    'Culture Valais',
    'validated',
    'active',
    'system_scraper',
    CURRENT_TIMESTAMP
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, end_date, categories, source_url, organizer_name, validation_status, status, creator_id, scraped_at)
VALUES (
    'De Manet',
    'Valais accueille cet événement. AutreVe 06.02. - Di 14.06.2026De Manetà KellyFondation Pierre Gianadda, MartignyEn savoir plusEn savoir plus',
    'Valais, Suisse',
    46.23067303265039,
    7.369165421050619,
    '2026-06-14',
    '2026-06-14',
    '["Culture > Expositions"]'::jsonb,
    'https://agenda.culturevalais.ch/fr/event/show/41813',
    'Culture Valais',
    'validated',
    'active',
    'system_scraper',
    CURRENT_TIMESTAMP
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, end_date, categories, source_url, organizer_name, validation_status, status, creator_id, scraped_at)
VALUES (
    'La mort, on en parle ?',
    'Rendez-vous à Valais. ConférenceSa 07.02. - Sa 07.03.2026La mort, on en parle ?soirée partageBibliothèque de Crans-Montana, Crans-MontanaEn savoir plusEn savoir plus',
    'Valais, Suisse',
    46.23292918601822,
    7.3641397630724015,
    '2026-03-07',
    '2026-03-07',
    '["Culture > Expositions", "Culture > Conf\u00e9rences & Rencontres"]'::jsonb,
    'https://agenda.culturevalais.ch/fr/event/show/41835',
    'Culture Valais',
    'validated',
    'active',
    'system_scraper',
    CURRENT_TIMESTAMP
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, end_date, categories, source_url, organizer_name, validation_status, status, creator_id, scraped_at)
VALUES (
    'Appel à projets artistiques – œuvres en extérieur',
    'Valais accueille cet événement. Appel à projets artistiques – œuvres en extérieurL’archipel à Sion lance un appel à projets ! 2 artistes valaisan·es créeront chacun·e une œuvre originale à partir de matériaux de la ressourcerie, lor...',
    'Valais, Suisse',
    46.23220280698925,
    7.369099398049055,
    NULL,
    NULL,
    '["Culture > Expositions"]'::jsonb,
    'https://agenda.culturevalais.ch/fr/news/show/13958',
    'Culture Valais',
    'validated',
    'active',
    'system_scraper',
    CURRENT_TIMESTAMP
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, end_date, categories, source_url, organizer_name, validation_status, status, creator_id, scraped_at)
VALUES (
    'Être artiste pédagogue aujourd''hui',
    'Rendez-vous à Valais pour cet événement. Je 05.03.2026Être artiste pédagogue aujourd''huiDéconstruire un système pour recommencer autrementJe 05.03.2026Être artiste pédagogue aujourd''huiDéconstruire un système pour recommencer autrementEn sav...',
    'Valais, Suisse',
    46.231633382424974,
    7.366164921290509,
    '2026-03-05',
    '2026-03-05',
    '["Culture > Expositions"]'::jsonb,
    'https://agenda.culturevalais.ch/fr/course/show/2231',
    'Culture Valais',
    'validated',
    'active',
    'system_scraper',
    CURRENT_TIMESTAMP
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, end_date, categories, source_url, organizer_name, validation_status, status, creator_id, scraped_at)
VALUES (
    'Die Kunst der Steuererklärung',
    'Valais accueille cet événement. Sa 14.03.2026Die Kunst der Steuererklärungfür KulturschaffendeSa 14.03.2026Die Kunst der Steuererklärungfür KulturschaffendeEn savoir plus',
    'Valais, Suisse',
    46.23210524975638,
    7.368353128457041,
    '2026-03-14',
    '2026-03-14',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://agenda.culturevalais.ch/fr/course/show/2181',
    'Culture Valais',
    'validated',
    'active',
    'system_scraper',
    CURRENT_TIMESTAMP
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, end_date, categories, source_url, organizer_name, validation_status, status, creator_id, scraped_at)
VALUES (
    'LuMaMeJeVeSaDi2627282930310102030405060708091011121314151617181920212223242526272801',
    'Valais accueille cet événement. LuMaMeJeVeSaDi2627282930310102030405060708091011121314151617181920212223242526272801',
    'Valais, Suisse',
    46.23334330315783,
    7.365872832372736,
    NULL,
    NULL,
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.sierre.ch/fr/calendrier-manifestations-1738/agenda-calendar-06022026.html',
    'Sierre Calendrier',
    'validated',
    'active',
    'system_scraper',
    CURRENT_TIMESTAMP
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, end_date, categories, source_url, organizer_name, validation_status, status, creator_id, scraped_at)
VALUES (
    'LuMaMeJeVeSaDi232425262728010203040506070809101112131415161718192021222324252627282930310102030405',
    'Valais accueille cet événement. LuMaMeJeVeSaDi232425262728010203040506070809101112131415161718192021222324252627282930310102030405',
    'Valais, Suisse',
    46.23274524778786,
    7.3680624124383,
    NULL,
    NULL,
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.sierre.ch/fr/calendrier-manifestations-1738/agenda-calendar-01032026.html',
    'Sierre Calendrier',
    'validated',
    'active',
    'system_scraper',
    CURRENT_TIMESTAMP
) ON CONFLICT DO NOTHING;
