# NordTrail Gear — Identifiants de démonstration

Utilisez ces identifiants pour tester les futurs outils MCP.

## Commandes par statut

| order_id | status | Scénario |
|----------|--------|----------|
| NTG-2026-000201 | livree | Retour ouvert — chaussures inconfort |
| NTG-2026-000202 | expediee | Veste en transit (express) |
| NTG-2026-000203 | en_preparation | Annulation possible |
| NTG-2026-000204 | annulee | Remboursée avant expédition |
| NTG-2026-000205 | retour_demande | Lampe défectueuse |
| NTG-2026-000208 | en_attente | Paiement non capturé (tente) |
| NTG-2026-000212 | livree | Retour refusé (hors délai) |

## Clients

| client_id | email | Note |
|-----------|-------|------|
| CL-004 | amina.diallo@example.ca | Commande chaussures livrée |
| CL-006 | luc.bergeron@example.ca | `risk_flags: retours_repetes` |
| CL-012 | isabelle.lavoie@example.ca | Gold — coupon VIP15 |
| CL-010 | chloe.martin@example.ca | Retour lampe en cours |

## Produits et stock

| product_id | Nom | Stock notable |
|------------|-----|----------------|
| NTG-SHOE-001 | TrailStorm X2 | **0** à WH-QC, 28 à WH-MTL |
| NTG-SHOE-003 | PeakRush Ultra 5 | Faible (3 à MTL) |
| NTG-TENT-001 | RidgeLite 2 | 4 / 2 / 3 par entrepôt |

## Coupons

| code | Résultat attendu |
|------|------------------|
| TRAIL20 | Actif — 20 %, min 150 CAD |
| SUMMIT10 | Inactif / expiré |
| VIP15 | Actif — réservé gold |
| SPRING25 | Actif — 25 CAD fixe |

## Retours

| return_id | status |
|-----------|--------|
| RET-2026-001 | pending (lampe) |
| RET-2026-002 | pending (chaussures) |
| RET-2025-089 | rejected (hors délai) |
