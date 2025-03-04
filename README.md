App to Track the Breaking Chains Sober Sundays disc golf league

* Has the following functions
  * User entry day of
  * New Score Entry
    * Webscrapes current round results from UDisc
    * Returns list of registered user's with database ids
    * The LD puts the right LD next to the right user from the UDisc results
      * This serves two functions: updating names to match udisc for consistency and assigning player place
    * This kicks off tag calculation and payout calculation
    * Redirects to results when completed
  * Delete User
    * Review screen for registered users with what they opted in for and what tag
    * Delete a user if wrong and re-enter.
    * Flashes message to confirm deletion or error.
  * Backup Score Entry
    * Enter places next to registered players.
    * This is a backup for if the udisc scrape fails.
    * This is a temporary resolution, the scrape issue should be resolved day of and New Score Entry should be ran to keep names consistent.
  * Results
     * Tabular results based off of score entry
  * CTP Wrapup
    * a list of the entered CTPs for the day
      * grouped by hole number
      * sorted oldest to newest
      * holder is highlighted in gray
    *  CTP Stub
      * site that just has image links to each CTP URL endpoint in the event that users cannot do the QR code.
    * Tag Summary
      * List of current issued tags and holders
      * Each user is a hyperlink to show historical tag activity
      * Each tag is a hyperlink to show histrical ownership 
   
  
   

 To do's
  * track ace pot value on registration page
    * on leage review page add button to cash out ace pot with confirmation
   
