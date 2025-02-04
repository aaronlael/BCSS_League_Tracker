App to Track the Breaking Chains Sober Sundays disc golf league

* Has the following functions
  * User entry day of
  * New Score Entry
    * Webscrapes current round results from UDisc
    * Returns list of registered user's with database ids
    * The LD puts the right LD next to the right user from the UDisc results
      * This serves two functions: updating names to match udisc for consistency and assigning player place
    * This kicks off tag calculation and payout calculation
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
 * Tag movement page
   * select a player to see all the tags they've held in the season in order - done
   * select a tag to see all the players who have held it in order - done
   * see a list of current tags with their current holder - done
   * Add csv export of round data for visualization
     * enhance scraping from Udisc to collect full round details for players
     * add weather, time, conditions details
     * track things like tag delta from start to end of round
   * track ace pot? 
