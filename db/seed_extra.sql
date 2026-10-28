-- Extra seed rows for the tables that are empty in ecommerce.sql
-- (deliveries, warranties, reviews, insurance, returns, payments, direct debits,
-- monthly best sellers). Load after ecommerce.sql:
--   docker exec -i chatbot_mariadb mariadb -uroot ecommerce < db/seed_extra.sql
-- All ids below refer to rows that exist in ecommerce.sql.

INSERT INTO livraisons (commande_id, tracking_number, carrier, status, shipped_date, delivery_date, delivery_address, recipient_name) VALUES
(1, 'TRACK-FR-001234567', 'Chronopost', 'delivered', '2026-01-16 09:00:00', '2026-01-17 14:30:00', '12 Rue de la Paix, 75001 Paris', 'Alice Martin'),
(2, 'TRACK-FR-002345678', 'Colissimo', 'delivered', '2026-01-17 10:00:00', '2026-01-19 11:15:00', '45 Avenue des Champs, 69001 Lyon', 'Robert Dupont'),
(3, 'TRACK-FR-003456789', 'UPS', 'in_transit', '2026-01-19 08:00:00', NULL, '78 Boulevard Haussmann, 13001 Marseille', 'Claire Bernard'),
(4, 'TRACK-FR-004567890', 'Chronopost', 'delivered', '2026-01-18 11:00:00', '2026-01-19 16:45:00', '12 Rue de la Paix, 75001 Paris', 'Alice Martin'),
(6, 'TRACK-FR-006789012', 'DHL', 'delivered', '2026-01-18 07:00:00', '2026-01-20 10:20:00', '56 Rue de Rivoli, 06000 Nice', 'Emma Petit'),
(9, 'TRACK-FR-009012345', 'Colissimo', 'delivered', '2026-01-20 09:30:00', '2026-01-22 15:00:00', '78 Boulevard Haussmann, 13001 Marseille', 'Claire Bernard'),
(10, 'TRACK-FR-010123456', 'Chronopost', 'shipped', '2026-01-21 08:00:00', NULL, '56 Rue de Rivoli, 06000 Nice', 'Emma Petit'),
(11, 'TRACK-FR-011234567', 'Colissimo', 'delivered', '2026-01-22 10:00:00', '2026-01-24 12:30:00', '12 Rue de la Paix, 75001 Paris', 'Alice Martin'),
(14, 'TRACK-FR-014567890', 'UPS', 'shipped', '2026-01-24 09:00:00', NULL, '89 Avenue Foch, 44000 Nantes', 'François Girard'),
(15, 'TRACK-FR-015678901', 'DHL', 'delivered', '2026-01-23 07:30:00', '2026-01-25 11:00:00', '56 Rue de Rivoli, 06000 Nice', 'Emma Petit');

INSERT INTO garanties (commande_item_id, type, start_date, end_date, coverage_details, status) VALUES
(1, 'constructeur', '2026-01-15', '2028-01-15', 'Garantie Apple 2 ans', 'active'),
(2, 'constructeur', '2026-01-15', '2028-01-15', 'Garantie Apple 2 ans', 'active'),
(3, 'constructeur', '2026-01-16', '2028-01-16', 'Garantie Sony 2 ans', 'active'),
(4, 'etendue', '2026-01-18', '2030-01-18', 'Garantie étendue 4 ans Dell', 'active'),
(10, 'constructeur', '2026-01-17', '2028-01-17', 'Garantie Sony 2 ans', 'active');

INSERT INTO assurances (commande_item_id, policy_number, insurance_company, coverage_type, monthly_premium, coverage_amount, start_date, end_date, status) VALUES
(1, 'ASSU-IP15PM-001', 'AppleCare+ France', 'complete', 12.99, 1299.99, '2026-01-15', '2028-01-15', 'active'),
(2, 'ASSU-MBP-001', 'AppleCare+ France', 'complete', 19.99, 2199.99, '2026-01-15', '2028-01-15', 'active'),
(4, 'ASSU-XPS15-001', 'Dell Premium Support', 'casse', 14.99, 1699.99, '2026-01-18', '2029-01-18', 'active'),
(10, 'ASSU-A7IV-001', 'Sony Imaging Protect', 'vol', 15.99, 2599.99, '2026-01-17', '2028-01-17', 'active');

INSERT INTO retours (commande_item_id, reason, description, status, resolution_date, refund_amount) VALUES
(3, 'not_satisfied', 'Qualité audio pas à la hauteur des attentes', 'refunded', '2026-01-25 00:00:00', 399.99),
(13, 'defective', 'Écran ne s''allume plus après 2 jours', 'approved', NULL, NULL);

INSERT INTO avis (produit_id, client_id, rating, title, comment, verified_purchase, helpful_count) VALUES
(1, 1, 5, 'Excellent téléphone!', 'Le meilleur iPhone à ce jour. Performance incroyable et appareil photo exceptionnel.', TRUE, 24),
(7, 1, 5, 'MacBook parfait', 'Puissance de la puce M3 impressionnante. Idéal pour le développement.', TRUE, 18),
(12, 2, 4, 'Très bon casque', 'Réduction de bruit excellente, mais un peu cher.', TRUE, 12),
(9, 3, 5, 'Le meilleur laptop', 'Dell XPS 15 est parfait pour le travail pro. Écran magnifique.', TRUE, 31),
(21, 4, 5, 'PS5 géniale', 'Graphismes incroyables et chargements ultra rapides.', TRUE, 45),
(17, 5, 5, 'Caméra professionnelle', 'Sony Alpha 7 IV dépasse toutes mes attentes. Qualité vidéo 4K exceptionnelle.', TRUE, 38),
(25, 1, 4, 'Bonne montre', 'Apple Watch Series 9 très pratique mais batterie pourrait être meilleure.', TRUE, 15),
(3, 3, 5, 'Samsung au top', 'Galaxy S24 Ultra avec S Pen est parfait pour les notes et créativité.', TRUE, 28),
(14, 1, 5, 'AirPods excellents', 'Qualité audio Apple incomparable. Réduction de bruit top.', TRUE, 22),
(15, 6, 4, 'Bonne enceinte', 'Bose SoundLink son à 360° impressionnant. Batterie longue durée.', FALSE, 9);

-- Invoice 15 does not exist in the dump (14 invoices), so that payment row is left out.
INSERT INTO paiements (facture_id, mode_paiement_id, amount, transaction_id, status) VALUES
(1, 1, 2500.00, 'TXN-20260115-001', 'success'),
(2, 4, 400.00, 'PP-20260116-123', 'success'),
(3, 1, 1000.00, 'TXN-20260118-045', 'success'),
(4, 1, 1100.00, 'TXN-20260117-098', 'success'),
(6, 3, 2350.00, 'SEPA-20260117-234', 'success'),
(9, 1, 850.00, 'TXN-20260119-156', 'success'),
(10, 1, 2950.00, 'TXN-20260120-289', 'success'),
(11, 4, 450.00, 'PP-20260121-456', 'success'),
(14, 1, 1000.00, 'TXN-20260123-567', 'success');

INSERT INTO prelevements (client_id, iban, bic, mandate_reference, mandate_date, status) VALUES
(1, 'FR7612345678901234567890123', 'BNPAFRPP', 'MAND-ALICE-001', '2025-12-01', 'active'),
(3, 'FR7698765432109876543210987', 'SOGEFRPP', 'MAND-CLAIRE-001', '2025-11-15', 'active'),
(5, 'FR7611112222333344445555666', 'CEPAFRPP', 'MAND-EMMA-001', '2025-10-20', 'active');

INSERT INTO best_products (produit_id, total_sold, revenue, avg_rating, review_count, month) VALUES
(1, 45, 58499.55, 5.00, 12, '2026-01-01'),
(3, 38, 45599.62, 5.00, 8, '2026-01-01'),
(7, 32, 70399.68, 5.00, 15, '2026-01-01'),
(9, 28, 47599.72, 5.00, 10, '2026-01-01'),
(12, 67, 26799.33, 4.50, 25, '2026-01-01'),
(14, 89, 24909.11, 5.00, 34, '2026-01-01'),
(21, 52, 28599.48, 5.00, 18, '2026-01-01'),
(17, 18, 46799.82, 5.00, 7, '2026-01-01'),
(25, 41, 18449.59, 4.00, 14, '2026-01-01'),
(33, 156, 9358.44, 4.80, 42, '2026-01-01');
