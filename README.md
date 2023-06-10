To run the code first install the required dependencies. Run the following command:


        pip install -r requirements.txt

To calculate the aggregate based on a formula, run the script with the desired formula as a command-line argument. For example:


    python Aggregation.py --formula "Q.N.I8.W1.S1.S1.T.A.FA.D.F._Z.EUR._T._X.N =Q.N.I8.W1.S1P.S1.T.A.FA.D.F._Z.EUR._T._X.N +Q.N.I8.W1.S1Q.S1.T.A.FA.D.F._Z.EUR._T._X.N"


This will compute the aggregate values based on the given formula and display the resulting DataFrame on the screen. The aggregated values will also be saved in a file named aggregate.csv.

Please make sure to have an internet connection while running the script to fetch the transaction data from the specified URL.


The Aggregations.py file consists of following functions :


    > def url_request(identifier: str)-> Response

        Helper function to send the request and return a response if not then the relevant exception 


    > def pivot_table(dfs, s, sign) -> List
        pivot_table is helping function used to create a DataFrame should use TIME_PERIOD column as the index, and have as many columns as there are identifiers, each containing values of the OBS_VALUE column from the appropriate DataFrame. Names of the
        columns are the names of the identifiers, in the order they appear in the formula.



    > get_transactions(identifier: str) -> DataFrame

        Function should fetch the transaction data from the appropriate URL and convert it to a pandas DataFrame, with
        columns IDENTIFIER, TIME_PERIOD and OBS_VALUE, corresponding to values of the identifier parameter,
        generic:ObsDimension tag and generic:ObsValue tag from the XML. OBS_VALUE should be converted to
        float.

        Example
        Running: get_transactions("Q.N.I8.W1.S1.S1.T.A.FA.D.F._Z.EUR._T._X.N") 
        
        Output :

                                IDENTIFIER             TIME_PERIOD        OBS_VALUE
        Q.N.I8.W1.S1.S1.T.A.FA.D.F._Z.EUR._T._X.N       1999-Q1          5420.181862
        Q.N.I8.W1.S1.S1.T.A.FA.D.F._Z.EUR._T._X.N       1999-Q2          87003.970961


    > def get_formula_data(formula: str) -> DataFrame

        The function should parse the formula and fetch the data (using the function from part #1) for the identifiers on the
        right-hand side of the = operator.
        Resulting DataFrame should use TIME_PERIOD column as the index, and have as many columns as there are
        identifiers, each containing values of the OBS_VALUE column from the appropriate DataFrame. Names of the
        columns are the names of the identifiers, in the order they appear in the formula.
    

        Example
        Running:

        get_formula_data("Q.N.I8.W1.S1.S1.T.A.FA.D.F._Z.EUR._T._X.N =
        Q.N.I8.W1.S1P.S1.T.A.FA.D.F._Z.EUR._T._X.N +
        Q.N.I8.W1.S1Q.S1.T.A.FA.D.F._Z.EUR._T._X.N")

        Output :
        TIME_PERIOD     Q.N.I8.W1.S1P.S1.T.A.FA.D.F._Z.EUR._T._X.N         Q.N.I8.W1.S1Q.S1.T.A.FA.D.F._Z.EUR._T._X.N
        2008-Q1                     158849.702543                                    158813.745366
        2008-Q2                     55317.060368                                      55136.813191


    > def compute_aggregates(formula: str) -> DataFrame

        The function should load the data using the function from part #2 and return a DataFrame, indexed by
        TIME_PERIOD, with a single column, whose name is the identifier on the left-hand side of the = operator. Values of
        this column are obtained by applying the appropriate operations, as indicated by the formula, on the retrieved data.

        Example
        Running:

        compute_aggregates("Q.N.I8.W1.S1.S1.T.A.FA.D.F._Z.EUR._T._X.N =
        Q.N.I8.W1.S1P.S1.T.A.FA.D.F._Z.EUR._T._X.N +
        Q.N.I8.W1.S1Q.S1.T.A.FA.D.F._Z.EUR._T._X.N")

        Output :
        TIME_PERIOD              Q.N.I8.W1.S1.S1.T.A.FA.D.F._Z.EUR._T._X.N
        2008-Q1                                 317663.447909
        2008-Q2                                 110453.873559
