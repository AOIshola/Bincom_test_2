# Bincom_test_2

- Polling Unit Results Page: This page displays results for a specific polling unit. You can access this page by navigating to http://localhost:8000/polling_unit/{polling_unit_id} in your web browser, where {polling_unit_id} is the ID of the polling unit you want to view.

For example, to view results for polling unit with ID 10, go to http://localhost:8000/polling_unit/10.

- Summed Polling Unit Results Page: This page shows the summed result for a selected local government. To access this page, you need to specify the Local Government Area (LGA) ID in the URL. Navigate to http://localhost:8000/sum_polling_units?lga_id={lga_id}, where {lga_id} is the ID of the desired local government.

For example, to view the summed result for LGA with ID 5, go to http://localhost:8000/sum_polling_units?lga_id=5.

*NB:* Ensure the database is properly set up (check file "bincom.sql" in repo) and update the necessary database connection credentials to make the script work as required.
