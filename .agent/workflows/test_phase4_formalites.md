---
description: Automated testing of Phase 4 (Formalités Management) using integrated browser
---

# Test Workflow - Phase 4: Formalités Management

This workflow tests the complete formalités management functionality including creation, viewing, editing, status updates, and cost calculation.

## Prerequisites
- Application must be running on http://localhost:5000
- Database must be initialized with test data
- At least one dossier must exist in the database

## Test Steps

### 1. Start the Flask application
```powershell
cd C:\Users\Admin\Documents\Repository\AGEN-OHADA-flask\AGEN-OHADA-FLASK
python run.py
```

### 2. Navigate to Formalités index page
- Open browser to http://localhost:5000/formalites
- Verify the page loads successfully
- Check that statistics cards are displayed (Total, À Faire, En Cours, Terminé, Coût Total)

### 3. Test filtering and search
- Test type filter (select "ENREGISTREMENT")
- Test status filter (select "A_FAIRE")
- Test search functionality (search by dossier number)
- Verify "Réinitialiser" button clears all filters

### 4. Create a new formalité
- Click "Nouvelle Formalité" button
- Fill in the form:
  - Select a dossier from dropdown
  - Select type: "ENREGISTREMENT"
  - Select status: "A_FAIRE"
  - Set date de dépôt (today's date)
  - Click "Calculer automatiquement" to estimate cost
  - Verify cost estimation appears
  - Add reference externe: "TEST-REF-001"
- Submit the form
- Verify redirect to detail view
- Verify success message appears

### 5. Test detail view
- Verify all formalité information is displayed correctly
- Check status badge is displayed
- Check progress bar shows correct percentage
- Verify financial information (Coût Estimé, Coût Réel)
- Verify timeline information (Délai estimé, Jours écoulés)

### 6. Test status update
- Click "Changer le statut" dropdown
- Select "EN_COURS"
- Verify status updates successfully
- Verify progress bar updates to 50%
- Change status to "DEPOSE"
- Verify date_depot is automatically set if not already set
- Change status to "TERMINE"
- Verify date_retour is automatically set if not already set
- Verify progress bar shows 100%

### 7. Test edit functionality
- Click "Modifier" button
- Update cout_reel field with actual cost
- Update reference_externe
- Submit the form
- Verify changes are saved
- Verify redirect back to detail view

### 8. Test list view with created formalité
- Navigate back to formalités index
- Verify the created formalité appears in the table
- Verify status badge displays correctly
- Verify cost information displays correctly
- Verify dates are formatted properly

### 9. Test cost calculator API
- Create another formalité
- Select type "HYPOTHEQUE"
- Click "Calculer automatiquement"
- Verify different calculation for hypothèque type
- Try with "RCCM" type
- Try with "JOURNAL" type
- Try with "CADASTRE" type

### 10. Test delete functionality
- From detail view, click "Supprimer" button
- Confirm deletion in the dialog
- Verify redirect to index page
- Verify formalité is removed from the list
- Verify success message appears

## Expected Results
- All CRUD operations work correctly
- Status workflow functions properly with automatic date updates
- Cost calculator provides accurate estimates for different formality types
- Filtering and search return correct results
- Statistics update dynamically
- All UI elements render properly with modern styling
- Navigation between views works seamlessly

## Success Criteria
✅ Can create formalités with all required fields
✅ Can view detailed information for each formalité
✅ Can update formalité information and status
✅ Can delete formalités
✅ Cost calculator provides estimates for all formality types
✅ Status workflow updates dates automatically
✅ Filtering and search work correctly
✅ Statistics display accurate information
✅ UI is responsive and modern
