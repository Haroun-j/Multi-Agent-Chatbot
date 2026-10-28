-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
--
-- Hôte : mariadb:3306
-- Généré le : jeu. 29 jan. 2026 à 11:56
-- Version du serveur : 12.1.2-MariaDB-ubu2404
-- Version de PHP : 8.3.30

SET FOREIGN_KEY_CHECKS=0;
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `ecommerce`
--

-- --------------------------------------------------------

--
-- Structure de la table `assurances`
--

CREATE TABLE IF NOT EXISTS `assurances` (
  `id` int(11) NOT NULL,
  `commande_item_id` int(11) NOT NULL,
  `policy_number` varchar(50) NOT NULL,
  `insurance_company` varchar(200) DEFAULT NULL,
  `coverage_type` enum('vol','casse','liquide','complete') DEFAULT 'complete',
  `monthly_premium` decimal(10,2) DEFAULT NULL,
  `coverage_amount` decimal(10,2) DEFAULT NULL,
  `start_date` date NOT NULL,
  `end_date` date DEFAULT NULL,
  `status` enum('active','suspended','cancelled','expired') DEFAULT 'active'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `avis`
--

CREATE TABLE IF NOT EXISTS `avis` (
  `id` int(11) NOT NULL,
  `produit_id` int(11) NOT NULL,
  `client_id` int(11) NOT NULL,
  `rating` int(11) DEFAULT NULL CHECK (`rating` between 1 and 5),
  `title` varchar(200) DEFAULT NULL,
  `comment` text DEFAULT NULL,
  `verified_purchase` tinyint(1) DEFAULT 0,
  `helpful_count` int(11) DEFAULT 0,
  `created_at` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `best_products`
--

CREATE TABLE IF NOT EXISTS `best_products` (
  `id` int(11) NOT NULL,
  `produit_id` int(11) NOT NULL,
  `total_sold` int(11) DEFAULT 0,
  `revenue` decimal(12,2) DEFAULT 0.00,
  `avg_rating` decimal(3,2) DEFAULT NULL,
  `review_count` int(11) DEFAULT 0,
  `month` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `categories`
--

CREATE TABLE IF NOT EXISTS `categories` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `image_url` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `categories`
--

INSERT INTO `categories` (`id`, `name`, `description`, `parent_id`, `image_url`) VALUES
(1, 'Smartphones', 'Téléphones mobiles et accessoires', NULL, NULL),
(2, 'Ordinateurs', 'PC portables et de bureau', NULL, NULL),
(3, 'Audio', 'Casques, enceintes et audio', NULL, NULL),
(4, 'Photo & Vidéo', 'Appareils photo et caméras', NULL, NULL),
(5, 'Gaming', 'Consoles et accessoires gaming', NULL, NULL),
(6, 'Wearables', 'Montres connectées et trackers', NULL, NULL),
(7, 'Smart Home', 'Maison connectée', NULL, NULL),
(8, 'Accessoires', 'Accessoires électroniques', NULL, NULL),
(9, 'iPhone', 'Smartphones Apple', 1, NULL),
(10, 'Android', 'Smartphones Android', 1, NULL),
(11, 'PC Portable', 'Ordinateurs portables', 2, NULL),
(12, 'PC Bureau', 'Ordinateurs de bureau', 2, NULL),
(13, 'Casques', 'Casques audio', 3, NULL),
(14, 'Enceintes', 'Enceintes Bluetooth', 3, NULL);

-- --------------------------------------------------------

--
-- Structure de la table `clients`
--

CREATE TABLE IF NOT EXISTS `clients` (
  `id` int(11) NOT NULL,
  `client_reference` varchar(13) DEFAULT NULL,
  `username` varchar(100) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) DEFAULT NULL,
  `first_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `postal_code` varchar(20) DEFAULT NULL,
  `country` varchar(100) DEFAULT 'France',
  `date_naissance` date DEFAULT NULL,
  `client_type` enum('particulier','professionnel','premium') DEFAULT 'particulier',
  `points_fidelite` int(11) DEFAULT 0,
  `created_at` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `clients`
--

INSERT INTO `clients` (`id`, `client_reference`, `username`, `email`, `password_hash`, `first_name`, `last_name`, `phone`, `address`, `city`, `postal_code`, `country`, `date_naissance`, `client_type`, `points_fidelite`, `created_at`) VALUES
(1, '1000000000123', 'alice_martin', 'alice.martin@gmail.com', 'hash_alice', 'Alice', 'Martin', '+33612345678', '12 Rue de la Paix', 'Paris', '75001', 'France', '1990-05-15', 'premium', 1250, '2026-01-28 22:16:34'),
(2, '1000000000456', 'bob_dupont', 'bob.dupont@yahoo.fr', 'hash_bob', 'Robert', 'Dupont', '+33623456789', '45 Avenue des Champs', 'Lyon', '69001', 'France', '1985-08-22', 'particulier', 340, '2026-01-28 22:16:34'),
(3, '1000000000789', 'claire_bernard', 'claire@entreprise.com', 'hash_claire', 'Claire', 'Bernard', '+33634567890', '78 Boulevard Haussmann', 'Marseille', '13001', 'France', '1992-12-03', 'professionnel', 850, '2026-01-28 22:16:34'),
(4, '1000000001012', 'david_roux', 'david.roux@hotmail.com', 'hash_david', 'David', 'Roux', '+33645678901', '23 Rue Victor Hugo', 'Toulouse', '31000', 'France', '1988-03-17', 'particulier', 120, '2026-01-28 22:16:34'),
(5, '1000000001345', 'emma_petit', 'emma.petit@gmail.com', 'hash_emma', 'Emma', 'Petit', '+33656789012', '56 Rue de Rivoli', 'Nice', '06000', 'France', '1995-07-29', 'premium', 2100, '2026-01-28 22:16:34'),
(6, '1000000001678', 'francois_girard', 'francois@email.fr', 'hash_francois', 'François', 'Girard', '+33667890123', '89 Avenue Foch', 'Nantes', '44000', 'France', '1982-11-08', 'particulier', 450, '2026-01-28 22:16:34');

-- --------------------------------------------------------

--
-- Structure de la table `commandes`
--

CREATE TABLE IF NOT EXISTS `commandes` (
  `id` int(11) NOT NULL,
  `client_id` int(11) NOT NULL,
  `order_number` varchar(50) NOT NULL,
  `status` enum('pending','confirmed','processing','shipped','delivered','cancelled','refunded') DEFAULT 'pending',
  `total_ht` decimal(10,2) DEFAULT NULL,
  `total_tva` decimal(10,2) DEFAULT NULL,
  `total_ttc` decimal(10,2) NOT NULL,
  `shipping_cost` decimal(10,2) DEFAULT 0.00,
  `coupon_id` int(11) DEFAULT NULL,
  `discount_amount` decimal(10,2) DEFAULT 0.00,
  `shipping_address` text DEFAULT NULL,
  `billing_address` text DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `commandes`
--

INSERT INTO `commandes` (`id`, `client_id`, `order_number`, `status`, `total_ht`, `total_tva`, `total_ttc`, `shipping_cost`, `coupon_id`, `discount_amount`, `shipping_address`, `billing_address`, `notes`, `created_at`, `updated_at`) VALUES
(1, 1, 'CMD-2026-0001', 'delivered', 2083.33, 416.67, 2500.00, 0.00, 1, 250.00, '12 Rue de la Paix, 75001 Paris', '12 Rue de la Paix, 75001 Paris', NULL, '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(2, 2, 'CMD-2026-0002', 'shipped', 333.33, 66.67, 400.00, 5.90, NULL, 0.00, '45 Avenue des Champs, 69001 Lyon', '45 Avenue des Champs, 69001 Lyon', NULL, '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(3, 3, 'CMD-2026-0003', 'processing', 1416.67, 283.33, 1700.00, 0.00, 2, 340.00, '78 Boulevard Haussmann, 13001 Marseille', '78 Boulevard Haussmann, 13001 Marseille', NULL, '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(4, 1, 'CMD-2026-0004', 'delivered', 916.67, 183.33, 1100.00, 7.50, 4, 165.00, '12 Rue de la Paix, 75001 Paris', '12 Rue de la Paix, 75001 Paris', NULL, '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(5, 4, 'CMD-2026-0005', 'confirmed', 625.00, 125.00, 750.00, 5.90, NULL, 0.00, '23 Rue Victor Hugo, 31000 Toulouse', '23 Rue Victor Hugo, 31000 Toulouse', NULL, '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(6, 5, 'CMD-2026-0006', 'delivered', 1958.33, 391.67, 2350.00, 0.00, 4, 350.00, '56 Rue de Rivoli, 06000 Nice', '56 Rue de Rivoli, 06000 Nice', NULL, '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(7, 2, 'CMD-2026-0007', 'cancelled', 166.67, 33.33, 200.00, 5.90, NULL, 0.00, '45 Avenue des Champs, 69001 Lyon', '45 Avenue des Champs, 69001 Lyon', NULL, '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(8, 6, 'CMD-2026-0008', 'processing', 458.33, 91.67, 550.00, 5.90, 6, 20.00, '89 Avenue Foch, 44000 Nantes', '89 Avenue Foch, 44000 Nantes', NULL, '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(9, 3, 'CMD-2026-0009', 'delivered', 708.33, 141.67, 850.00, 7.50, NULL, 0.00, '78 Boulevard Haussmann, 13001 Marseille', '78 Boulevard Haussmann, 13001 Marseille', NULL, '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(10, 5, 'CMD-2026-0010', 'shipped', 2458.33, 491.67, 2950.00, 0.00, 5, 590.00, '56 Rue de Rivoli, 06000 Nice', '56 Rue de Rivoli, 06000 Nice', NULL, '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(11, 1, 'CMD-2026-0011', 'delivered', 375.00, 75.00, 450.00, 5.90, NULL, 0.00, '12 Rue de la Paix, 75001 Paris', '12 Rue de la Paix, 75001 Paris', NULL, '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(12, 4, 'CMD-2026-0012', 'processing', 1083.33, 216.67, 1300.00, 7.50, 1, 130.00, '23 Rue Victor Hugo, 31000 Toulouse', '23 Rue Victor Hugo, 31000 Toulouse', NULL, '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(13, 2, 'CMD-2026-0013', 'confirmed', 291.67, 58.33, 350.00, 5.90, NULL, 0.00, '45 Avenue des Champs, 69001 Lyon', '45 Avenue des Champs, 69001 Lyon', NULL, '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(14, 6, 'CMD-2026-0014', 'shipped', 833.33, 166.67, 1000.00, 5.90, 4, 150.00, '89 Avenue Foch, 44000 Nantes', '89 Avenue Foch, 44000 Nantes', NULL, '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(15, 5, 'CMD-2026-0015', 'delivered', 1625.00, 325.00, 1950.00, 0.00, NULL, 0.00, '56 Rue de Rivoli, 06000 Nice', '56 Rue de Rivoli, 06000 Nice', NULL, '2026-01-28 22:16:34', '2026-01-28 22:16:34');

-- --------------------------------------------------------

--
-- Structure de la table `commande_items`
--

CREATE TABLE IF NOT EXISTS `commande_items` (
  `id` int(11) NOT NULL,
  `commande_id` int(11) NOT NULL,
  `produit_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL,
  `prix_unitaire` decimal(10,2) NOT NULL,
  `discount_percentage` decimal(5,2) DEFAULT 0.00,
  `total` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `commande_items`
--

INSERT INTO `commande_items` (`id`, `commande_id`, `produit_id`, `quantity`, `prix_unitaire`, `discount_percentage`, `total`) VALUES
(1, 1, 1, 1, 1299.99, 0.00, 1299.99),
(2, 1, 7, 1, 2199.99, 0.00, 2199.99),
(3, 2, 12, 1, 399.99, 0.00, 399.99),
(4, 3, 9, 1, 1699.99, 20.00, 1359.99),
(5, 3, 35, 1, 109.99, 0.00, 109.99),
(6, 3, 38, 1, 219.99, 0.00, 219.99),
(7, 4, 25, 1, 449.99, 15.00, 382.49),
(8, 4, 14, 1, 279.99, 15.00, 237.99),
(9, 5, 21, 1, 549.99, 0.00, 549.99),
(10, 6, 17, 1, 2599.99, 0.00, 2599.99),
(11, 7, 28, 1, 159.99, 0.00, 159.99),
(12, 8, 30, 1, 249.99, 0.00, 249.99),
(13, 8, 31, 1, 179.99, 0.00, 179.99),
(14, 9, 19, 1, 449.99, 0.00, 449.99),
(15, 9, 33, 1, 59.99, 0.00, 59.99),
(16, 9, 34, 2, 79.99, 0.00, 159.98),
(17, 10, 7, 1, 2199.99, 0.00, 2199.99),
(18, 10, 37, 1, 119.99, 0.00, 119.99),
(19, 11, 15, 1, 269.99, 0.00, 269.99),
(20, 12, 3, 1, 1199.99, 10.00, 1079.99),
(21, 13, 28, 1, 159.99, 0.00, 159.99),
(22, 14, 23, 1, 349.99, 0.00, 349.99),
(23, 14, 33, 2, 59.99, 0.00, 119.98),
(24, 15, 9, 1, 1699.99, 0.00, 1699.99),
(25, 15, 36, 1, 219.99, 0.00, 219.99);

-- --------------------------------------------------------

--
-- Structure de la table `coupons`
--

CREATE TABLE IF NOT EXISTS `coupons` (
  `id` int(11) NOT NULL,
  `code` varchar(50) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `discount_type` enum('percentage','fixed') DEFAULT 'percentage',
  `discount_value` decimal(10,2) NOT NULL,
  `min_purchase` decimal(10,2) DEFAULT 0.00,
  `max_discount` decimal(10,2) DEFAULT NULL,
  `usage_limit` int(11) DEFAULT NULL,
  `used_count` int(11) DEFAULT 0,
  `valid_from` timestamp NULL DEFAULT current_timestamp(),
  `valid_until` timestamp NULL DEFAULT NULL,
  `active` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `coupons`
--

INSERT INTO `coupons` (`id`, `code`, `description`, `discount_type`, `discount_value`, `min_purchase`, `max_discount`, `usage_limit`, `used_count`, `valid_from`, `valid_until`, `active`) VALUES
(1, 'WELCOME10', 'Bienvenue - 10% de réduction', 'percentage', 10.00, 50.00, 50.00, 100, 23, '2026-01-28 22:16:34', '2026-12-31 23:59:59', 1),
(2, 'TECH20', '20% sur high-tech', 'percentage', 20.00, 200.00, 100.00, 50, 12, '2026-01-28 22:16:34', '2026-06-30 23:59:59', 1),
(3, 'SUMMER50', '50€ de réduction été', 'fixed', 50.00, 300.00, 50.00, 200, 45, '2026-01-28 22:16:34', '2026-08-31 23:59:59', 1),
(4, 'PREMIUM15', 'Premium clients - 15%', 'percentage', 15.00, 100.00, 150.00, NULL, 67, '2026-01-28 22:16:34', NULL, 1),
(5, 'FLASH30', 'Flash sale 30%', 'percentage', 30.00, 500.00, 200.00, 30, 8, '2026-01-28 22:16:34', '2026-02-15 23:59:59', 1),
(6, 'STUDENT20', 'Étudiants - 20€', 'fixed', 20.00, 100.00, 20.00, 500, 134, '2026-01-28 22:16:34', '2026-12-31 23:59:59', 1);

-- --------------------------------------------------------

--
-- Structure de la table `factures`
--

CREATE TABLE IF NOT EXISTS `factures` (
  `id` int(11) NOT NULL,
  `commande_id` int(11) NOT NULL,
  `facture_number` varchar(50) NOT NULL,
  `date_emission` timestamp NULL DEFAULT current_timestamp(),
  `date_echeance` timestamp NULL DEFAULT NULL,
  `status` enum('unpaid','partial','paid','overdue','cancelled') DEFAULT 'unpaid',
  `total_ht` decimal(10,2) DEFAULT NULL,
  `total_tva` decimal(10,2) DEFAULT NULL,
  `total_ttc` decimal(10,2) NOT NULL,
  `pdf_url` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `factures`
--

INSERT INTO `factures` (`id`, `commande_id`, `facture_number`, `date_emission`, `date_echeance`, `status`, `total_ht`, `total_tva`, `total_ttc`, `pdf_url`) VALUES
(1, 1, 'FACT-2026-0001', '2026-01-28 22:16:34', '2026-02-15 00:00:00', 'paid', 2083.33, 416.67, 2500.00, NULL),
(2, 2, 'FACT-2026-0002', '2026-01-28 22:16:34', '2026-02-16 00:00:00', 'paid', 333.33, 66.67, 400.00, NULL),
(3, 3, 'FACT-2026-0003', '2026-01-28 22:16:34', '2026-02-20 00:00:00', 'partial', 1416.67, 283.33, 1700.00, NULL),
(4, 4, 'FACT-2026-0004', '2026-01-28 22:16:34', '2026-02-18 00:00:00', 'paid', 916.67, 183.33, 1100.00, NULL),
(5, 5, 'FACT-2026-0005', '2026-01-28 22:16:34', '2026-03-01 00:00:00', 'unpaid', 625.00, 125.00, 750.00, NULL),
(6, 6, 'FACT-2026-0006', '2026-01-28 22:16:34', '2026-02-17 00:00:00', 'paid', 1958.33, 391.67, 2350.00, NULL),
(7, 8, 'FACT-2026-0008', '2026-01-28 22:16:34', '2026-02-25 00:00:00', 'unpaid', 458.33, 91.67, 550.00, NULL),
(8, 9, 'FACT-2026-0009', '2026-01-28 22:16:34', '2026-02-19 00:00:00', 'paid', 708.33, 141.67, 850.00, NULL),
(9, 10, 'FACT-2026-0010', '2026-01-28 22:16:34', '2026-02-21 00:00:00', 'paid', 2458.33, 491.67, 2950.00, NULL),
(10, 11, 'FACT-2026-0011', '2026-01-28 22:16:34', '2026-02-22 00:00:00', 'paid', 375.00, 75.00, 450.00, NULL),
(11, 12, 'FACT-2026-0012', '2026-01-28 22:16:34', '2026-03-05 00:00:00', 'unpaid', 1083.33, 216.67, 1300.00, NULL),
(12, 13, 'FACT-2026-0013', '2026-01-28 22:16:34', '2026-02-28 00:00:00', 'unpaid', 291.67, 58.33, 350.00, NULL),
(13, 14, 'FACT-2026-0014', '2026-01-28 22:16:34', '2026-02-24 00:00:00', 'paid', 833.33, 166.67, 1000.00, NULL),
(14, 15, 'FACT-2026-0015', '2026-01-28 22:16:34', '2026-02-23 00:00:00', 'paid', 1625.00, 325.00, 1950.00, NULL);

-- --------------------------------------------------------

--
-- Structure de la table `fournisseurs`
--

CREATE TABLE IF NOT EXISTS `fournisseurs` (
  `id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  `contact_name` varchar(100) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `fournisseurs`
--

INSERT INTO `fournisseurs` (`id`, `name`, `contact_name`, `email`, `phone`, `address`, `city`, `country`, `created_at`) VALUES
(1, 'Apple France', 'Jean Dupuis', 'contact@apple.fr', '+33140400000', '9 Rue Porte de Bagneux', 'Paris', 'France', '2026-01-28 22:16:34'),
(2, 'Samsung Europe', 'Marie Schmidt', 'info@samsung.eu', '+33155550000', 'Tour Samsung', 'Lyon', 'France', '2026-01-28 22:16:34'),
(3, 'Sony Distribution', 'Pierre Leclerc', 'sales@sony.fr', '+33144440000', '25 Rue de la Gare', 'Marseille', 'France', '2026-01-28 22:16:34'),
(4, 'Dell Technologies', 'Laura Rossi', 'orders@dell.fr', '+33133330000', '34 Avenue Tech', 'Nantes', 'France', '2026-01-28 22:16:34'),
(5, 'Bose SARL', 'Michel Bernard', 'contact@bose.fr', '+33122220000', '12 Rue Audio', 'Nice', 'France', '2026-01-28 22:16:34');

-- --------------------------------------------------------

--
-- Structure de la table `garanties`
--

CREATE TABLE IF NOT EXISTS `garanties` (
  `id` int(11) NOT NULL,
  `commande_item_id` int(11) NOT NULL,
  `type` enum('constructeur','etendue','casse','vol') DEFAULT 'constructeur',
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `coverage_details` text DEFAULT NULL,
  `status` enum('active','expired','used','cancelled') DEFAULT 'active'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `livraisons`
--

CREATE TABLE IF NOT EXISTS `livraisons` (
  `id` int(11) NOT NULL,
  `commande_id` int(11) NOT NULL,
  `tracking_number` varchar(100) DEFAULT NULL,
  `carrier` varchar(100) DEFAULT NULL,
  `status` enum('preparing','shipped','in_transit','out_for_delivery','delivered','failed') DEFAULT 'preparing',
  `shipped_date` timestamp NULL DEFAULT NULL,
  `delivery_date` timestamp NULL DEFAULT NULL,
  `delivery_address` text DEFAULT NULL,
  `recipient_name` varchar(200) DEFAULT NULL,
  `signature_required` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `modes_paiement`
--

CREATE TABLE IF NOT EXISTS `modes_paiement` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `type` enum('card','transfer','direct_debit','paypal','cash','check') NOT NULL,
  `active` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `modes_paiement`
--

INSERT INTO `modes_paiement` (`id`, `name`, `type`, `active`) VALUES
(1, 'Carte Bancaire', 'card', 1),
(2, 'Virement Bancaire', 'transfer', 1),
(3, 'Prélèvement SEPA', 'direct_debit', 1),
(4, 'PayPal', 'paypal', 1),
(5, 'Espèces', 'cash', 1),
(6, 'Chèque', 'check', 1);

-- --------------------------------------------------------

--
-- Structure de la table `paiements`
--

CREATE TABLE IF NOT EXISTS `paiements` (
  `id` int(11) NOT NULL,
  `facture_id` int(11) NOT NULL,
  `mode_paiement_id` int(11) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `transaction_id` varchar(100) DEFAULT NULL,
  `status` enum('pending','success','failed','refunded') DEFAULT 'pending',
  `payment_date` timestamp NULL DEFAULT current_timestamp(),
  `notes` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `prelevements`
--

CREATE TABLE IF NOT EXISTS `prelevements` (
  `id` int(11) NOT NULL,
  `client_id` int(11) NOT NULL,
  `iban` varchar(34) NOT NULL,
  `bic` varchar(11) DEFAULT NULL,
  `mandate_reference` varchar(50) NOT NULL,
  `mandate_date` date DEFAULT NULL,
  `status` enum('active','suspended','cancelled') DEFAULT 'active',
  `created_at` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `produits`
--

CREATE TABLE IF NOT EXISTS `produits` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `category_id` int(11) DEFAULT NULL,
  `fournisseur_id` int(11) DEFAULT NULL,
  `prix_achat` decimal(10,2) DEFAULT NULL,
  `prix_vente` decimal(10,2) NOT NULL,
  `sku` varchar(100) DEFAULT NULL,
  `barcode` varchar(100) DEFAULT NULL,
  `brand` varchar(100) DEFAULT NULL,
  `model` varchar(100) DEFAULT NULL,
  `warranty_months` int(11) DEFAULT 24,
  `image_url` varchar(255) DEFAULT NULL,
  `specifications` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`specifications`)),
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `produits`
--

INSERT INTO `produits` (`id`, `name`, `description`, `category_id`, `fournisseur_id`, `prix_achat`, `prix_vente`, `sku`, `barcode`, `brand`, `model`, `warranty_months`, `image_url`, `specifications`, `created_at`, `updated_at`) VALUES
(1, 'iPhone 15 Pro Max 256GB', 'Dernier iPhone avec puce A17 Pro', 1, 1, 950.00, 1299.99, 'APL-IP15PM-256', NULL, 'Apple', 'iPhone 15 Pro Max', 24, NULL, '{\"screen\": \"6.7 inch\", \"storage\": \"256GB\", \"camera\": \"48MP\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(2, 'iPhone 15 128GB', 'iPhone 15 version standard', 1, 1, 700.00, 969.99, 'APL-IP15-128', NULL, 'Apple', 'iPhone 15', 24, NULL, '{\"screen\": \"6.1 inch\", \"storage\": \"128GB\", \"camera\": \"48MP\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(3, 'Samsung Galaxy S24 Ultra', 'Flagship Samsung avec S Pen', 1, 2, 850.00, 1199.99, 'SAM-S24U-512', NULL, 'Samsung', 'Galaxy S24 Ultra', 24, NULL, '{\"screen\": \"6.8 inch\", \"storage\": \"512GB\", \"camera\": \"200MP\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(4, 'Samsung Galaxy S24', 'Samsung Galaxy dernière génération', 1, 2, 600.00, 859.99, 'SAM-S24-256', NULL, 'Samsung', 'Galaxy S24', 24, NULL, '{\"screen\": \"6.2 inch\", \"storage\": \"256GB\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(5, 'Google Pixel 8 Pro', 'Smartphone Google IA avancée', 1, 2, 650.00, 899.99, 'GOO-PIX8P-256', NULL, 'Google', 'Pixel 8 Pro', 24, NULL, '{\"screen\": \"6.7 inch\", \"AI\": \"Google Tensor G3\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(6, 'OnePlus 12', 'Flagship OnePlus performance', 1, 2, 550.00, 799.99, 'ONP-OP12-256', NULL, 'OnePlus', 'OnePlus 12', 24, NULL, '{\"screen\": \"6.82 inch\", \"charging\": \"100W\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(7, 'MacBook Pro M3 14\"', 'MacBook Pro puce M3', 2, 1, 1600.00, 2199.99, 'APL-MBP14-M3', NULL, 'Apple', 'MacBook Pro 14\"', 24, NULL, '{\"processor\": \"M3\", \"ram\": \"16GB\", \"storage\": \"512GB\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(8, 'MacBook Air M2', 'MacBook Air léger et puissant', 2, 1, 1000.00, 1399.99, 'APL-MBA-M2', NULL, 'Apple', 'MacBook Air', 24, NULL, '{\"processor\": \"M2\", \"ram\": \"8GB\", \"storage\": \"256GB\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(9, 'Dell XPS 15', 'PC portable haute performance', 2, 4, 1200.00, 1699.99, 'DEL-XPS15-I9', NULL, 'Dell', 'XPS 15', 36, NULL, '{\"processor\": \"Intel i9\", \"ram\": \"32GB\", \"gpu\": \"RTX 4060\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(10, 'Dell XPS 13', 'Ultrabook compact et puissant', 2, 4, 900.00, 1299.99, 'DEL-XPS13-I7', NULL, 'Dell', 'XPS 13', 36, NULL, '{\"processor\": \"Intel i7\", \"ram\": \"16GB\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(11, 'ASUS ROG Zephyrus', 'PC portable gaming premium', 2, 4, 1400.00, 1999.99, 'ASU-ROGZ-RTX', NULL, 'ASUS', 'ROG Zephyrus', 24, NULL, '{\"processor\": \"AMD Ryzen 9\", \"gpu\": \"RTX 4080\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(12, 'Sony WH-1000XM5', 'Casque à réduction de bruit', 3, 3, 280.00, 399.99, 'SON-WH1000XM5', NULL, 'Sony', 'WH-1000XM5', 24, NULL, '{\"noise_cancelling\": \"yes\", \"battery\": \"30h\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(13, 'Bose QuietComfort Ultra', 'Casque premium Bose', 3, 5, 320.00, 449.99, 'BOS-QCULT', NULL, 'Bose', 'QuietComfort Ultra', 24, NULL, '{\"noise_cancelling\": \"yes\", \"spatial_audio\": \"yes\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(14, 'AirPods Pro 2', 'Écouteurs sans fil Apple', 3, 1, 180.00, 279.99, 'APL-AIRP2', NULL, 'Apple', 'AirPods Pro 2', 12, NULL, '{\"noise_cancelling\": \"yes\", \"transparency\": \"yes\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(15, 'Bose SoundLink Revolve+', 'Enceinte portable 360°', 3, 5, 180.00, 269.99, 'BOS-SLRP', NULL, 'Bose', 'SoundLink Revolve+', 12, NULL, '{\"battery\": \"16h\", \"waterproof\": \"yes\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(16, 'JBL Charge 5', 'Enceinte Bluetooth puissante', 3, 5, 100.00, 179.99, 'JBL-CHG5', NULL, 'JBL', 'Charge 5', 12, NULL, '{\"battery\": \"20h\", \"powerbank\": \"yes\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(17, 'Sony Alpha 7 IV', 'Appareil photo hybride professionnel', 4, 3, 1800.00, 2599.99, 'SON-A7IV', NULL, 'Sony', 'Alpha 7 IV', 24, NULL, '{\"sensor\": \"33MP\", \"video\": \"4K 60fps\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(18, 'Canon EOS R6 Mark II', 'Hybride Canon haute performance', 4, 3, 1900.00, 2699.99, 'CAN-R6M2', NULL, 'Canon', 'EOS R6 II', 24, NULL, '{\"sensor\": \"24MP\", \"fps\": \"40fps\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(19, 'GoPro Hero 12', 'Caméra action 5.3K', 4, 3, 300.00, 449.99, 'GOP-H12', NULL, 'GoPro', 'Hero 12', 12, NULL, '{\"video\": \"5.3K\", \"waterproof\": \"10m\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(20, 'DJI Mini 4 Pro', 'Drone compact 4K', 4, 3, 600.00, 859.99, 'DJI-MIN4P', NULL, 'DJI', 'Mini 4 Pro', 12, NULL, '{\"video\": \"4K 60fps\", \"range\": \"25km\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(21, 'PlayStation 5', 'Console Sony nouvelle génération', 5, 3, 400.00, 549.99, 'SON-PS5', NULL, 'Sony', 'PlayStation 5', 24, NULL, '{\"storage\": \"825GB SSD\", \"ray_tracing\": \"yes\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(22, 'Xbox Series X', 'Console Microsoft 4K', 5, 3, 400.00, 549.99, 'MSF-XBSX', NULL, 'Microsoft', 'Xbox Series X', 24, NULL, '{\"storage\": \"1TB SSD\", \"fps\": \"120fps\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(23, 'Nintendo Switch OLED', 'Console portable Nintendo', 5, 3, 280.00, 349.99, 'NIN-SWOLED', NULL, 'Nintendo', 'Switch OLED', 12, NULL, '{\"screen\": \"7 inch OLED\", \"battery\": \"9h\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(24, 'Steam Deck', 'Console portable PC gaming', 5, 3, 350.00, 469.99, 'VAL-STDK-512', NULL, 'Valve', 'Steam Deck', 12, NULL, '{\"storage\": \"512GB\", \"screen\": \"7 inch\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(25, 'Apple Watch Series 9', 'Montre connectée Apple', 6, 1, 320.00, 449.99, 'APL-AWS9-45', NULL, 'Apple', 'Watch Series 9', 12, NULL, '{\"size\": \"45mm\", \"gps\": \"yes\", \"cellular\": \"yes\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(26, 'Samsung Galaxy Watch 6', 'Montre Samsung Wear OS', 6, 2, 250.00, 359.99, 'SAM-GW6-44', NULL, 'Samsung', 'Galaxy Watch 6', 12, NULL, '{\"size\": \"44mm\", \"battery\": \"40h\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(27, 'Garmin Fenix 7', 'Montre sport GPS', 6, 2, 500.00, 699.99, 'GAR-FEN7', NULL, 'Garmin', 'Fenix 7', 24, NULL, '{\"gps\": \"multi-band\", \"battery\": \"18 days\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(28, 'Fitbit Charge 6', 'Bracelet fitness tracker', 6, 2, 100.00, 159.99, 'FIT-CHG6', NULL, 'Fitbit', 'Charge 6', 12, NULL, '{\"heart_rate\": \"yes\", \"gps\": \"yes\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(29, 'Google Nest Hub Max', 'Écran connecté Google', 7, 2, 150.00, 229.99, 'GOO-NHMAX', NULL, 'Google', 'Nest Hub Max', 12, NULL, '{\"screen\": \"10 inch\", \"camera\": \"yes\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(30, 'Amazon Echo Show 10', 'Écran Alexa rotatif', 7, 2, 180.00, 249.99, 'AMZ-ES10', NULL, 'Amazon', 'Echo Show 10', 12, NULL, '{\"screen\": \"10.1 inch\", \"rotation\": \"yes\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(31, 'Philips Hue Starter Kit', 'Kit éclairage connecté', 7, 2, 120.00, 179.99, 'PHI-HUEKIT', NULL, 'Philips', 'Hue White & Color', 24, NULL, '{\"bulbs\": \"3\", \"bridge\": \"yes\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(32, 'Ring Video Doorbell Pro', 'Sonnette vidéo connectée', 7, 2, 150.00, 229.99, 'RNG-VDBP', NULL, 'Ring', 'Doorbell Pro 2', 12, NULL, '{\"video\": \"1536p\", \"poe\": \"yes\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(33, 'Anker PowerBank 20000mAh', 'Batterie externe rapide', 8, 2, 35.00, 59.99, 'ANK-PB20K', NULL, 'Anker', 'PowerCore 20K', 18, NULL, '{\"capacity\": \"20000mAh\", \"ports\": \"2 USB-C\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(34, 'SanDisk microSD 512GB', 'Carte mémoire haute vitesse', 8, 2, 45.00, 79.99, 'SAN-SD512', NULL, 'SanDisk', 'Extreme Pro', 24, NULL, '{\"capacity\": \"512GB\", \"speed\": \"170MB/s\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(35, 'Logitech MX Master 3S', 'Souris ergonomique pro', 8, 2, 70.00, 109.99, 'LOG-MXM3S', NULL, 'Logitech', 'MX Master 3S', 12, NULL, '{\"dpi\": \"8000\", \"buttons\": \"7\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(36, 'Samsung T7 SSD 2TB', 'SSD externe portable', 8, 2, 140.00, 219.99, 'SAM-T7-2TB', NULL, 'Samsung', 'T7', 36, NULL, '{\"capacity\": \"2TB\", \"speed\": \"1050MB/s\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(37, 'Apple Magic Keyboard', 'Clavier sans fil Apple', 8, 1, 80.00, 119.99, 'APL-MGKB', NULL, 'Apple', 'Magic Keyboard', 12, NULL, '{\"bluetooth\": \"yes\", \"battery\": \"1 month\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34'),
(38, 'Belkin 3-in-1 Charger', 'Chargeur sans fil multi-appareils', 8, 1, 90.00, 149.99, 'BEL-3N1CHG', NULL, 'Belkin', '3-in-1 Stand', 12, NULL, '{\"wireless\": \"yes\", \"devices\": \"3\"}', '2026-01-28 22:16:34', '2026-01-28 22:16:34');

-- --------------------------------------------------------

--
-- Structure de la table `produits_promotions`
--

CREATE TABLE IF NOT EXISTS `produits_promotions` (
  `produit_id` int(11) NOT NULL,
  `promotion_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `produits_promotions`
--

INSERT INTO `produits_promotions` (`produit_id`, `promotion_id`) VALUES
(1, 2),
(2, 2),
(3, 2),
(4, 2),
(21, 3),
(22, 3),
(23, 3),
(7, 4),
(8, 4),
(9, 4),
(10, 4);

-- --------------------------------------------------------

--
-- Structure de la table `promotions`
--

CREATE TABLE IF NOT EXISTS `promotions` (
  `id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  `description` text DEFAULT NULL,
  `promo_type` enum('flash_sale','bundle','buy_x_get_y','seasonal') DEFAULT 'flash_sale',
  `discount_percentage` decimal(5,2) DEFAULT NULL,
  `start_date` timestamp NULL DEFAULT current_timestamp(),
  `end_date` timestamp NULL DEFAULT NULL,
  `active` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `promotions`
--

INSERT INTO `promotions` (`id`, `name`, `description`, `promo_type`, `discount_percentage`, `start_date`, `end_date`, `active`) VALUES
(1, 'Black Friday 2026', 'Méga promotions Black Friday', 'flash_sale', 40.00, '2026-11-27 00:00:00', '2026-11-30 23:59:59', 1),
(2, 'Soldes Hiver', 'Soldes d\'hiver électronique', 'seasonal', 25.00, '2026-01-15 00:00:00', '2026-02-15 23:59:59', 1),
(3, 'Pack Gaming', 'Console + 2 jeux', 'bundle', 15.00, '2026-01-01 00:00:00', '2026-03-31 23:59:59', 1),
(4, 'Offre Rentrée', 'Spécial rentrée scolaire', 'seasonal', 20.00, '2026-08-15 00:00:00', '2026-09-30 23:59:59', 0);

-- --------------------------------------------------------

--
-- Structure de la table `retours`
--

CREATE TABLE IF NOT EXISTS `retours` (
  `id` int(11) NOT NULL,
  `commande_item_id` int(11) NOT NULL,
  `reason` enum('defective','wrong_item','not_satisfied','damaged','other') NOT NULL,
  `description` text DEFAULT NULL,
  `status` enum('requested','approved','rejected','received','refunded') DEFAULT 'requested',
  `request_date` timestamp NULL DEFAULT current_timestamp(),
  `resolution_date` timestamp NULL DEFAULT NULL,
  `refund_amount` decimal(10,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `stock`
--

CREATE TABLE IF NOT EXISTS `stock` (
  `id` int(11) NOT NULL,
  `produit_id` int(11) NOT NULL,
  `quantity` int(11) DEFAULT 0,
  `reserved` int(11) DEFAULT 0,
  `disponible` int(11) GENERATED ALWAYS AS (`quantity` - `reserved`) STORED,
  `location` varchar(100) DEFAULT NULL,
  `last_restock` timestamp NULL DEFAULT current_timestamp(),
  `min_stock` int(11) DEFAULT 5,
  `max_stock` int(11) DEFAULT 100
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `stock`
--

INSERT INTO `stock` (`id`, `produit_id`, `quantity`, `reserved`, `location`, `last_restock`, `min_stock`, `max_stock`) VALUES
(1, 1, 25, 3, 'A-12', '2026-01-28 22:16:34', 5, 50),
(2, 2, 40, 5, 'A-13', '2026-01-28 22:16:34', 10, 80),
(3, 3, 18, 2, 'A-14', '2026-01-28 22:16:34', 5, 40),
(4, 4, 35, 4, 'A-15', '2026-01-28 22:16:34', 10, 60),
(5, 5, 22, 1, 'A-16', '2026-01-28 22:16:34', 5, 40),
(6, 6, 30, 3, 'A-17', '2026-01-28 22:16:34', 8, 50),
(7, 7, 15, 2, 'B-01', '2026-01-28 22:16:34', 3, 30),
(8, 8, 28, 4, 'B-02', '2026-01-28 22:16:34', 5, 50),
(9, 9, 12, 1, 'B-03', '2026-01-28 22:16:34', 3, 25),
(10, 10, 20, 2, 'B-04', '2026-01-28 22:16:34', 5, 40),
(11, 11, 8, 1, 'B-05', '2026-01-28 22:16:34', 2, 20),
(12, 12, 45, 6, 'C-01', '2026-01-28 22:16:34', 10, 80),
(13, 13, 38, 4, 'C-02', '2026-01-28 22:16:34', 8, 70),
(14, 14, 60, 8, 'C-03', '2026-01-28 22:16:34', 15, 100),
(15, 15, 25, 3, 'C-04', '2026-01-28 22:16:34', 5, 50),
(16, 16, 35, 4, 'C-05', '2026-01-28 22:16:34', 8, 60),
(17, 17, 12, 1, 'D-01', '2026-01-28 22:16:34', 3, 25),
(18, 18, 10, 1, 'D-02', '2026-01-28 22:16:34', 2, 20),
(19, 19, 18, 2, 'D-03', '2026-01-28 22:16:34', 4, 35),
(20, 20, 14, 1, 'D-04', '2026-01-28 22:16:34', 3, 30),
(21, 21, 22, 3, 'E-01', '2026-01-28 22:16:34', 5, 40),
(22, 22, 20, 2, 'E-02', '2026-01-28 22:16:34', 5, 35),
(23, 23, 30, 4, 'E-03', '2026-01-28 22:16:34', 8, 50),
(24, 24, 15, 2, 'E-04', '2026-01-28 22:16:34', 3, 30),
(25, 25, 28, 3, 'F-01', '2026-01-28 22:16:34', 6, 50),
(26, 26, 32, 4, 'F-02', '2026-01-28 22:16:34', 8, 60),
(27, 27, 18, 2, 'F-03', '2026-01-28 22:16:34', 4, 35),
(28, 28, 40, 5, 'F-04', '2026-01-28 22:16:34', 10, 70),
(29, 29, 35, 4, 'G-01', '2026-01-28 22:16:34', 8, 60),
(30, 30, 28, 3, 'G-02', '2026-01-28 22:16:34', 6, 50),
(31, 31, 50, 6, 'G-03', '2026-01-28 22:16:34', 12, 80),
(32, 32, 42, 5, 'G-04', '2026-01-28 22:16:34', 10, 70),
(33, 33, 80, 10, 'H-01', '2026-01-28 22:16:34', 20, 150),
(34, 34, 65, 8, 'H-02', '2026-01-28 22:16:34', 15, 120),
(35, 35, 55, 6, 'H-03', '2026-01-28 22:16:34', 12, 100),
(36, 36, 48, 5, 'H-04', '2026-01-28 22:16:34', 10, 90),
(37, 37, 70, 8, 'H-05', '2026-01-28 22:16:34', 15, 120),
(38, 38, 45, 5, 'H-06', '2026-01-28 22:16:34', 10, 80);

-- --------------------------------------------------------

--
-- Structure de la table `users`
--

CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) NOT NULL,
  `username` varchar(100) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) DEFAULT NULL,
  `role` enum('admin','manager','sales','support') DEFAULT 'support',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `last_login` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `role`, `created_at`, `last_login`) VALUES
(1, 'admin', 'admin@electrostore.fr', 'hash_admin_123', 'admin', '2026-01-28 22:16:33', NULL),
(2, 'marie_manager', 'marie@electrostore.fr', 'hash_marie_456', 'manager', '2026-01-28 22:16:33', NULL),
(3, 'jean_sales', 'jean@electrostore.fr', 'hash_jean_789', 'sales', '2026-01-28 22:16:33', NULL),
(4, 'sophie_support', 'sophie@electrostore.fr', 'hash_sophie_012', 'support', '2026-01-28 22:16:33', NULL);

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `assurances`
--
ALTER TABLE `assurances`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `policy_number` (`policy_number`),
  ADD KEY `commande_item_id` (`commande_item_id`),
  ADD KEY `idx_status` (`status`);

--
-- Index pour la table `avis`
--
ALTER TABLE `avis`
  ADD PRIMARY KEY (`id`),
  ADD KEY `client_id` (`client_id`),
  ADD KEY `idx_rating` (`rating`),
  ADD KEY `idx_produit` (`produit_id`);

--
-- Index pour la table `best_products`
--
ALTER TABLE `best_products`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_product_month` (`produit_id`,`month`),
  ADD KEY `idx_revenue` (`revenue` DESC),
  ADD KEY `idx_sold` (`total_sold` DESC);

--
-- Index pour la table `categories`
--
ALTER TABLE `categories`
  ADD PRIMARY KEY (`id`),
  ADD KEY `parent_id` (`parent_id`);

--
-- Index pour la table `clients`
--
ALTER TABLE `clients`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `client_reference` (`client_reference`),
  ADD KEY `idx_email` (`email`),
  ADD KEY `idx_client_type` (`client_type`);

--
-- Index pour la table `commandes`
--
ALTER TABLE `commandes`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `order_number` (`order_number`),
  ADD KEY `coupon_id` (`coupon_id`),
  ADD KEY `idx_client` (`client_id`),
  ADD KEY `idx_status` (`status`),
  ADD KEY `idx_date` (`created_at`);

--
-- Index pour la table `commande_items`
--
ALTER TABLE `commande_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `commande_id` (`commande_id`),
  ADD KEY `produit_id` (`produit_id`);

--
-- Index pour la table `coupons`
--
ALTER TABLE `coupons`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `code` (`code`),
  ADD KEY `idx_code` (`code`);

--
-- Index pour la table `factures`
--
ALTER TABLE `factures`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `facture_number` (`facture_number`),
  ADD KEY `commande_id` (`commande_id`),
  ADD KEY `idx_status` (`status`),
  ADD KEY `idx_date` (`date_emission`);

--
-- Index pour la table `fournisseurs`
--
ALTER TABLE `fournisseurs`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `garanties`
--
ALTER TABLE `garanties`
  ADD PRIMARY KEY (`id`),
  ADD KEY `commande_item_id` (`commande_item_id`),
  ADD KEY `idx_status` (`status`),
  ADD KEY `idx_dates` (`start_date`,`end_date`);

--
-- Index pour la table `livraisons`
--
ALTER TABLE `livraisons`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `tracking_number` (`tracking_number`),
  ADD KEY `commande_id` (`commande_id`),
  ADD KEY `idx_status` (`status`);

--
-- Index pour la table `modes_paiement`
--
ALTER TABLE `modes_paiement`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `paiements`
--
ALTER TABLE `paiements`
  ADD PRIMARY KEY (`id`),
  ADD KEY `facture_id` (`facture_id`),
  ADD KEY `mode_paiement_id` (`mode_paiement_id`),
  ADD KEY `idx_status` (`status`),
  ADD KEY `idx_date` (`payment_date`);

--
-- Index pour la table `prelevements`
--
ALTER TABLE `prelevements`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `mandate_reference` (`mandate_reference`),
  ADD KEY `client_id` (`client_id`);

--
-- Index pour la table `produits`
--
ALTER TABLE `produits`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `sku` (`sku`),
  ADD KEY `fournisseur_id` (`fournisseur_id`),
  ADD KEY `idx_category` (`category_id`),
  ADD KEY `idx_price` (`prix_vente`);

--
-- Index pour la table `produits_promotions`
--
ALTER TABLE `produits_promotions`
  ADD PRIMARY KEY (`produit_id`,`promotion_id`),
  ADD KEY `promotion_id` (`promotion_id`);

--
-- Index pour la table `promotions`
--
ALTER TABLE `promotions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_dates` (`start_date`,`end_date`);

--
-- Index pour la table `retours`
--
ALTER TABLE `retours`
  ADD PRIMARY KEY (`id`),
  ADD KEY `commande_item_id` (`commande_item_id`),
  ADD KEY `idx_status` (`status`);

--
-- Index pour la table `stock`
--
ALTER TABLE `stock`
  ADD PRIMARY KEY (`id`),
  ADD KEY `produit_id` (`produit_id`),
  ADD KEY `idx_disponible` (`disponible`);

--
-- Index pour la table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `assurances`
--
ALTER TABLE `assurances`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `avis`
--
ALTER TABLE `avis`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `best_products`
--
ALTER TABLE `best_products`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `categories`
--
ALTER TABLE `categories`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT pour la table `clients`
--
ALTER TABLE `clients`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT pour la table `commandes`
--
ALTER TABLE `commandes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT pour la table `commande_items`
--
ALTER TABLE `commande_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=26;

--
-- AUTO_INCREMENT pour la table `coupons`
--
ALTER TABLE `coupons`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT pour la table `factures`
--
ALTER TABLE `factures`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT pour la table `fournisseurs`
--
ALTER TABLE `fournisseurs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT pour la table `garanties`
--
ALTER TABLE `garanties`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `livraisons`
--
ALTER TABLE `livraisons`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `modes_paiement`
--
ALTER TABLE `modes_paiement`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT pour la table `paiements`
--
ALTER TABLE `paiements`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT pour la table `prelevements`
--
ALTER TABLE `prelevements`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `produits`
--
ALTER TABLE `produits`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=39;

--
-- AUTO_INCREMENT pour la table `promotions`
--
ALTER TABLE `promotions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT pour la table `retours`
--
ALTER TABLE `retours`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `stock`
--
ALTER TABLE `stock`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=39;

--
-- AUTO_INCREMENT pour la table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `assurances`
--
ALTER TABLE `assurances`
  ADD CONSTRAINT `1` FOREIGN KEY (`commande_item_id`) REFERENCES `commande_items` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `avis`
--
ALTER TABLE `avis`
  ADD CONSTRAINT `1` FOREIGN KEY (`produit_id`) REFERENCES `produits` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `2` FOREIGN KEY (`client_id`) REFERENCES `clients` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `best_products`
--
ALTER TABLE `best_products`
  ADD CONSTRAINT `1` FOREIGN KEY (`produit_id`) REFERENCES `produits` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `categories`
--
ALTER TABLE `categories`
  ADD CONSTRAINT `1` FOREIGN KEY (`parent_id`) REFERENCES `categories` (`id`) ON DELETE SET NULL;

--
-- Contraintes pour la table `commandes`
--
ALTER TABLE `commandes`
  ADD CONSTRAINT `1` FOREIGN KEY (`client_id`) REFERENCES `clients` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `2` FOREIGN KEY (`coupon_id`) REFERENCES `coupons` (`id`) ON DELETE SET NULL;

--
-- Contraintes pour la table `commande_items`
--
ALTER TABLE `commande_items`
  ADD CONSTRAINT `1` FOREIGN KEY (`commande_id`) REFERENCES `commandes` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `2` FOREIGN KEY (`produit_id`) REFERENCES `produits` (`id`);

--
-- Contraintes pour la table `factures`
--
ALTER TABLE `factures`
  ADD CONSTRAINT `1` FOREIGN KEY (`commande_id`) REFERENCES `commandes` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `garanties`
--
ALTER TABLE `garanties`
  ADD CONSTRAINT `1` FOREIGN KEY (`commande_item_id`) REFERENCES `commande_items` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `livraisons`
--
ALTER TABLE `livraisons`
  ADD CONSTRAINT `1` FOREIGN KEY (`commande_id`) REFERENCES `commandes` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `paiements`
--
ALTER TABLE `paiements`
  ADD CONSTRAINT `1` FOREIGN KEY (`facture_id`) REFERENCES `factures` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `2` FOREIGN KEY (`mode_paiement_id`) REFERENCES `modes_paiement` (`id`);

--
-- Contraintes pour la table `prelevements`
--
ALTER TABLE `prelevements`
  ADD CONSTRAINT `1` FOREIGN KEY (`client_id`) REFERENCES `clients` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `produits`
--
ALTER TABLE `produits`
  ADD CONSTRAINT `1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `2` FOREIGN KEY (`fournisseur_id`) REFERENCES `fournisseurs` (`id`) ON DELETE SET NULL;

--
-- Contraintes pour la table `produits_promotions`
--
ALTER TABLE `produits_promotions`
  ADD CONSTRAINT `1` FOREIGN KEY (`produit_id`) REFERENCES `produits` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `2` FOREIGN KEY (`promotion_id`) REFERENCES `promotions` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `retours`
--
ALTER TABLE `retours`
  ADD CONSTRAINT `1` FOREIGN KEY (`commande_item_id`) REFERENCES `commande_items` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `stock`
--
ALTER TABLE `stock`
  ADD CONSTRAINT `1` FOREIGN KEY (`produit_id`) REFERENCES `produits` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

SET FOREIGN_KEY_CHECKS=1; COMMIT;
