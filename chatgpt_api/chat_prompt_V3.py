# Define the latest available time period for data querying
latest_time_period = "2024q3"

# Background and Table Structure
overall_task_instructions = """
```
Task Description:
The task is to transform the natural language query into a SQL query for SQLite database.
This involves parsing the intent of the query and understanding the structure of the data to generate an appropriate SQL command.
```
"""

# Detailed overview of the table to guide the model
database_overview_instructions = f"""
```
Database Overview:
- The Database is information from 30 tables of the NPORT dataset. 
- The data includes a comprehensive view of fund-level information, holdings, debt securities, repurchase agreements, and derivative instruments.
- Each relation represents detailed information about financial transactions, security holdings, and fund performance, including key identifiers like ACCESSION_NUMBER, HOLDING_ID, and CUSIP for borrowers, holdings, and securities.
- The table provides essential metrics like total assets, liabilities, interest rate risks, monthly returns, and details for securities lending and collateral.
- The table aggregates all the data to provide a holistic view of financial activities for the 2019q4 to 2024q3 period.
```
"""

# Schema information as plain text with descriptions for each column in the database
schema_info = """
```
Schema description:
Below is the schema description of all tables and their attributes

Table: SUBMISSION
    - This table contains information from the EDGAR(Electronic Data Gathering, Analysis, and Retrieval) submission
    - ACCESSION_NUMBER (Primary Key): 
        This is a 20-character identifier that is unique to every document 
        submitted to the SEC (Securities and Exchange Commission) through the EDGAR system. 
        The first 10 digits represent the entity making the filing, 
        followed by the filing year (24 for 2024), and the sequence of the filing.
        This unique number allows users and regulators to track this specific report.
    - FILING_DATE: 
        This is the date when the report was officially submitted to the SEC, 
        meaning the fund handed in its NPORT report on this specific filling date.
    - FILE_NUM: 
        File number associated with the filing which is used to uniquely track and 
        categorize the registration and regulatory documents of the investment 
        company with the SEC.
    - SUB_TYPE: 
        Type of the submission, including the following types.
        NPORT-P: standard monthly report.
        NPORT-P/A: an amendment to correct or update a previously filed NPORT-P.
        NT NPORT-P: a notification that the regular NPORT-P filing will be late, requesting more time to submit it.
    - REPORT_ENDING_PERIOD: 
        This is the final date of the period covered by the report. 
        It is the date of fiscal year-end for the report, which marks the 
        end of the company's or fund's business year for financial reporting purposes.
    - REPORT_DATE: 
        Specific date on which the financial and portfolio data provided in the report 
        are accurate and reflect the fund's holdings and performance. 
    - IS_LAST_FILING: 
        This field indicates whether this is the fund's final report. 
        'N' means this is not the last report for the fund, and the fund will continue to submit future reports.

Table: REGISTRANT 
    - This table contains information about the registrant
    - ACCESSION_NUMBER (Primary Key): 
        This is a 20-character identifier that is unique to every document 
        submitted to the SEC (Securities and Exchange Commission) through the EDGAR system. 
        The first 10 digits represent the entity making the filing, 
        followed by the filing year (24 for 2024), and the sequence of the filing.
        This unique number allows users and regulators to track this specific report.
    - CIK:
        CIK stands for Central Index Key. It is a 10-digit number assigned by the SEC 
        to companies and individuals submitting filings through EDGAR, used to uniquely identify them.
    - REGISTRANT_NAME:
        The official name of the entity or individual registering with the SEC.
    - FILE_NUM:
        This is the Investment Company Act file number, assigned to registrants like investment 
        companies or mutual funds, used to track filings under the Investment Company Act.
    - LEI:
        LEI stands for Legal Entity Identifier, which is a 20-character alphanumeric code 
        used globally to identify legal entities participating in financial transactions. 
        It helps in tracking and identifying companies across various markets.
    - ADDRESS1:
        The first line of the registrant's mailing address. It typically includes the street address.
    - ADDRESS2:
        The second line of the registrant's mailing address, 
        usually used for additional address information like an apartment or suite number.
    - CITY:
        The city where the registrant's address is located.
    - STATE:
        The state where the registrant's address is located.
    - COUNTRY:
        The country where the registrant's address is located.
    - ZIP:
        The ZIP code or postal code of the registrant's address.
    - PHONE:
        The phone number for the registrant.

Table: FUND_REPORTED_INFO
    - This table contains information about the fund
    - ACCESSION_NUMBER (Primary Key): 
        This is a 20-character identifier that is unique to every document 
        submitted to the SEC (Securities and Exchange Commission) through the EDGAR system. 
        The first 10 digits represent the entity making the filing, 
        followed by the filing year (24 for 2024), and the sequence of the filing.
        This unique number allows users and regulators to track this specific report.
    - SERIES_NAME:
        The official name assigned to the series or individual fund within a larger fund family.
    - SERIES_ID: 
        The EDGAR Series Identifier, which uniquely distinguishes each series within the SEC's database.
    - SERIES_LEI: 
        The Legal Entity Identifier (LEI) of the series, a globally recognized ID used in financial transactions.
    - TOTAL_ASSETS: 
        The complete value of the fund's assets, including cash, securities, and other investments, measured in monetary terms.
    - TOTAL_LIABILITIES: 
        The aggregate value of the fund's debts or obligations.
    - NET_ASSETS: 
        Calculated as total assets minus total liabilities, this value represents the fund's equity available to shareholders, 
        reflecting its true economic value.
    - ASSETS_ATTRBT_TO_MISC_SECURITY: 
        Assets that are attributed to miscellaneous securities that don't fall under main asset classes.
    - ASSETS_INVESTED: 
        Refers to fund assets invested in a Controlled Foreign Corporation (CFC), 
        which are entities in foreign jurisdictions where the fund holds a controlling interest.
    - BORROWING_PAY_WITHIN_1YR: 
        The total amount the fund owes to banks or other financial institutions for short-term loans, repayable within one year. 
    - CTRLD_COMPANIES_PAY_WITHIN_1YR: 
        The amount payable within one year to affiliated companies controlled by the same parent company.
    - OTHER_AFFILIA_PAY_WITHIN_1YR: 
        Short-term amounts payable to other affiliates not directly controlled by the parent company.
    - OTHER_PAY_WITHIN_1YR: 
        Total amount due within one year to non-affiliated third parties, 
        which may include service providers, suppliers, or other unrelated creditors.
    - BORROWING_PAY_AFTER_1YR: 
        Total value of long-term debt to financial institutions, which is due for repayment beyond one year.
    - CTRLD_COMPANIES_PAY_AFTER_1YR: 
        Long-term debt obligations to controlled companies, repayable after one year. 
    - OTHER_AFFILIA_PAY_AFTER_1YR: 
        Payables due after one year to related parties outside the controlled group, 
        reflecting long-term service or operational arrangements.
    - OTHER_PAY_AFTER_1YR: 
        Total long-term obligations to unrelated parties, not due within the next year.
    - DELAYED_DELIVERY: 
        Represents payables for securities bought under delayed delivery agreements, often where settlement is postponed.
    - STANDBY_COMMITMENT: 
        Payables arising from standby commitments, which are agreements granting the option to buy securities.
    - LIQUIDATION_PREFERENCE: 
        The preferred stock's claim on assets in a liquidation scenario, where this stock class has a priority claim over common shareholders.
    - CASH_NOT_RPTD_IN_C_OR_D: 
        Represents cash holdings or equivalents that haven't been categorized in specific asset parts (Parts C or D).
    - CREDIT_SPREAD_3MON_INVEST: 
        The change in value of the portfolio resulting from a 1 basis point change in credit spreads where the shift is applied 
        to the option adjusted spread, aggregated by investment grade for 3 month maturity.
    - CREDIT_SPREAD_1YR_INVEST:
        The change in value of the portfolio resulting from a 1 basis point change in credit spreads where the shift is applied 
        to the option adjusted spread, aggregated by investment grade for 1 year maturity.
    - CREDIT_SPREAD_5YR_INVEST:
        The change in value of the portfolio resulting from a 1 basis point change in credit spreads where the shift is applied 
        to the option adjusted spread, aggregated by investment grade for 5 year maturity.
    - CREDIT_SPREAD_10YR_INVEST:
        The change in value of the portfolio resulting from a 1 basis point change in credit spreads where the shift is applied 
        to the option adjusted spread, aggregated by investment grade for 10 year maturity.
    - CREDIT_SPREAD_30YR_INVEST:
        The change in value of the portfolio resulting from a 1 basis point change in credit spreads where the shift is applied 
        to the option adjusted spread, aggregated by investment grade for 30 year maturity.
    - CREDIT_SPREAD_3MON_NONINVEST:
        The change in value of the portfolio resulting from a 1 basis point change in credit spreads where the shift is applied
        to the option adjusted spread, aggregated by non investment grade for 3 month maturity.
    - CREDIT_SPREAD_1YR_NONINVEST:
        The change in value of the portfolio resulting from a 1 basis point change in credit spreads where the shift is applied
        to the option adjusted spread, aggregated by non investment grade for 1 year maturity.
    - CREDIT_SPREAD_5YR_NONINVEST:
        The change in value of the portfolio resulting from a 1 basis point change in credit spreads where the shift is applied
        to the option adjusted spread, aggregated by non investment grade for 5 year maturity.
    - CREDIT_SPREAD_10YR_NONINVEST:
        The change in value of the portfolio resulting from a 1 basis point change in credit spreads where the shift is applied
        to the option adjusted spread, aggregated by non investment grade for 10 year maturity.
    - CREDIT_SPREAD_30YR_NONINVEST:
        The change in value of the portfolio resulting from a 1 basis point change in credit spreads where the shift is applied
        to the option adjusted spread, aggregated by non investment grade for 30 year maturity.
    - IS_NON_CASH_COLLATERAL: 
        This field indicates whether any securities lending counterparties have provided non-cash collateral. 
        A "yes" (Y) or "no" (N) value in this field shows if any part of the collateral received by the fund for loaned securities 
        consists of non-cash items, such as securities rather than cash, which the fund may treat as assets.
    - NET_REALIZE_GAIN_NONDERIV_MON1: 
        This column captures the net realized gain or loss from non-derivative investments for the first month in the reporting period. 
        Realized gains occur when assets are sold for more than the purchase price, 
        while losses reflect sales at a price lower than the original purchase.
    - NET_UNREALIZE_AP_NONDERIV_MON1: 
        This column indicates the net change in unrealized appreciation or depreciation for non-derivative investments in the first month. 
        Unrealized appreciation (or depreciation) reflects the increase or decrease in market value of holdings that the fund has not yet sold.
    - NET_REALIZE_GAIN_NONDERIV_MON2: 
        This column captures the net realized gain or loss from non-derivative investments for the second month in the reporting period. 
        Realized gains occur when assets are sold for more than the purchase price, 
        while losses reflect sales at a price lower than the original purchase.
    - NET_UNREALIZE_AP_NONDERIV_MON2: 
        This column indicates the net change in unrealized appreciation or depreciation for non-derivative investments in the second month. 
        Unrealized appreciation (or depreciation) reflects the increase or decrease in market value of holdings that the fund has not yet sold.
    - - NET_REALIZE_GAIN_NONDERIV_MON3: 
        This column captures the net realized gain or loss from non-derivative investments for the third month in the reporting period. 
        Realized gains occur when assets are sold for more than the purchase price, 
        while losses reflect sales at a price lower than the original purchase.
    - NET_UNREALIZE_AP_NONDERIV_MON3: 
        This column indicates the net change in unrealized appreciation or depreciation for non-derivative investments in the third month. 
        Unrealized appreciation (or depreciation) reflects the increase or decrease in market value of holdings that the fund has not yet sold.
    - SALES_FLOW_MON1: 
        This column reflects the total net asset value (NAV) of shares sold by the fund in the first month, 
        showing new inflows from investor purchases of fund shares.
    - REINVESTMENT_FLOW_MON1: 
        This field reports the NAV of shares sold in the first month due to reinvestments of dividends and distributions. 
        It indicates how much of the cash distributed to shareholders is reinvested into the fund, growing its asset base.
    - REDEMPTION_FLOW_MON1: 
        This captures the NAV of shares redeemed or repurchased, including exchanges, during the first month. 
        Redemptions represent investor outflows as shares are sold back to the fund.
    - SALES_FLOW_MON2: 
        This column reflects the total net asset value (NAV) of shares sold by the fund in the second month, 
        showing new inflows from investor purchases of fund shares.
    - REINVESTMENT_FLOW_MON2: 
        This field reports the NAV of shares sold in the second month due to reinvestments of dividends and distributions. 
        It indicates how much of the cash distributed to shareholders is reinvested into the fund, growing its asset base.
    - REDEMPTION_FLOW_MON2: 
        This captures the NAV of shares redeemed or repurchased, including exchanges, during the second month. 
        Redemptions represent investor outflows as shares are sold back to the fund.
    - SALES_FLOW_MON3: 
        This column reflects the total net asset value (NAV) of shares sold by the fund in the third month, 
        showing new inflows from investor purchases of fund shares.
    - REINVESTMENT_FLOW_MON3: 
        This field reports the NAV of shares sold in the third month due to reinvestments of dividends and distributions. 
        It indicates how much of the cash distributed to shareholders is reinvested into the fund, growing its asset base.
    - REDEMPTION_FLOW_MON3: 
        This captures the NAV of shares redeemed or repurchased, including exchanges, during the third month. 
        Redemptions represent investor outflows as shares are sold back to the fund.

Table: INTEREST_RATE_RISK
    - This table contains information about interest rate risk
    - ACCESSION_NUMBER (Dual Primary Key): 
        This is a 20-character identifier that is unique to every document 
        submitted to the SEC (Securities and Exchange Commission) through the EDGAR system. 
        The first 10 digits represent the entity making the filing, 
        followed by the filing year (24 for 2024), and the sequence of the filing.
        This unique number allows users and regulators to track this specific report.
    - INTEREST_RATE_RISK_ID (Dual Primary Key): 
        This is a surrogate key, which is an artificially created unique identifier for each record in this table. 
        It distinguishes multiple records related to interest rate risks within the same filing.
    - CURRENCY_CODE: 
        This column represents the currency in which the interest rate risk is reported (e.g., USD, EUR, JPY). 
    - INTRST_RATE_CHANGE_3MON_DV01:
        Change in value of the portfolio resulting from a 1 basis point change in interest rates for maturity in 3 months.
    - INTRST_RATE_CHANGE_1YR_DV01:
        Change in value of the portfolio resulting from a 1 basis point change in interest rates for maturity in 1 year.
    - INTRST_RATE_CHANGE_5YR_DV01:
        Change in value of the portfolio resulting from a 1 basis point change in interest rates for maturity in 5 year.
    - INTRST_RATE_CHANGE_10YR_DV01:
        Change in value of the portfolio resulting from a 1 basis point change in interest rates for maturity in 10 year.
    - INTRST_RATE_CHANGE_30YR_DV01:
        Change in value of the portfolio resulting from a 1 basis point change in interest rates for maturity in 30 year.
    - INTRST_RATE_CHANGE_3MON_DV100:
        Change in value of the portfolio resulting from a 100 basis point change in interest rates for maturity in 3 months.
    - INTRST_RATE_CHANGE_1YR_DV100:
        Change in value of the portfolio resulting from a 100 basis point change in interest rates for maturity in 1 year.
    - INTRST_RATE_CHANGE_5YR_DV100:
        Change in value of the portfolio resulting from a 100 basis point change in interest rates for maturity in 5 year.
    - INTRST_RATE_CHANGE_10YR_DV100:
        Change in value of the portfolio resulting from a 100 basis point change in interest rates for maturity in 10 year.
    - INTRST_RATE_CHANGE_30YR_DV100:
        Change in value of the portfolio resulting from a 100 basis point change in interest rates for maturity in 30 year.

Table: BORROWER
    - This table contains information for each borrower in a securities lending transaction
    - ACCESSION_NUMBER (Dual Primary Key): 
        This is a 20-character identifier that is unique to every document 
        submitted to the SEC (Securities and Exchange Commission) through the EDGAR system. 
        The first 10 digits represent the entity making the filing, 
        followed by the filing year (24 for 2024), and the sequence of the filing.
        This unique number allows users and regulators to track this specific report.
    - BORROWER_ID (Dual Primary Key):
        This is a surrogate key, which is an artificially created unique identifier for each record in this table. 
        It helps distinguish multiple borrowers under the same filing.
    - NAME: 
        This column records the name of the borrower involved in the securities lending transaction, such as a bank or financial institution.
    - LEI:
        The Legal Entity Identifier (LEI) of the borrower. LEIs are global identifiers for entities participating in financial transactions, 
        ensuring a standardized way to identify each borrower across different systems.
    - AGGREGATE_VALUE:
        This field shows the total value of all securities on loan to this specific borrower. 
        It provides insight into the scale of the lending activity involving each borrower, reflecting their financial engagement in the securities loan.

Table: BORROW_AGGREGATE
    - This table contains information for each category of non-cash collateral received for loaned securities
    - ACCESSION_NUMBER (Dual Primary Key): 
        This is a 20-character identifier that is unique to every document 
        submitted to the SEC (Securities and Exchange Commission) through the EDGAR system. 
        The first 10 digits represent the entity making the filing, 
        followed by the filing year (24 for 2024), and the sequence of the filing.
        This unique number allows users and regulators to track this specific report.
    - BORROW_AGGREGATE_ID: 
        This is a surrogate key serves as a unique identifier for each entry within a particular filing, 
        distinguishing each type of non-cash collateral received for securities lending within a single EDGAR submission.
    - AMOUNT: 
        This field records the aggregate principal amount of the collateral provided by the borrower. 
        This value gives a quantifiable measure of the collateral's nominal worth, providing an overview of the total exposure secured by the collateral.
    - COLLATERAL: 
        This column captures the aggregate value of the collateral provided, which may differ from the principal amount due to market or fair value adjustments. 
        It reflects the total worth of the collateral, as recognized by the fund.
    - INVESTMENT_CAT: 
        This column specifies the category or type of the collateral provided. 
        Common categories include well-defined asset classes such as UST (U.S. Treasury securities).

Table: MONTHLY_TOTAL_RETURN 
    - This table contains monthly total return information for each of the preceding three months.
    - ACCESSION_NUMBER (Primary Key): 
        This is a 20-character identifier that is unique to every document 
        submitted to the SEC (Securities and Exchange Commission) through the EDGAR system. 
        The first 10 digits represent the entity making the filing, 
        followed by the filing year (24 for 2024), and the sequence of the filing.
        This unique number allows users and regulators to track this specific report.
    - MONTHLY_TOTAL_RETURN_ID (Primary Key):
        Surrogate Key. This is a surrogate key that uniquely identifies each record of monthly total returns 
        within the table. Surrogate keys are often used to ensure that each entry has a distinct identity, 
        independent of the business logic.
    - CLASS_ID: 
        An identifier (if any) representing the classification of the fund or investment classes for which the returns are reported.
    - MONTHLY_TOTAL_RETURN1: 
        The total return for the fund for the first month of the reporting period.
    - MONTHLY_TOTAL_RETURN2: 
        The total return for the fund for the second month of the reporting period.
    - MONTHLY_TOTAL_RETURN3: 
        The total return for the fund for the third month of the reporting period.

Table: MONTHLY_RETURN_CAT_INSTRUMENT 
    - This table contains monthly return information attributable to derivatives for each of the preceding three month.
    - ACCESSION_NUMBER (Primary Key): 
        This is a 20-character identifier that is unique to every document 
        submitted to the SEC (Securities and Exchange Commission) through the EDGAR system. 
        The first 10 digits represent the entity making the filing, 
        followed by the filing year (24 for 2024), and the sequence of the filing.
        This unique number allows users and regulators to track this specific report.
    - ASSET_CAT (Primary Key):
        This column categorizes the asset type to which the derivatives belong (e.g., equities, bonds, commodities).
    - INSTRUMENT_KIND (Primary Key):
         Type of derivatives instrument associated with the asset category, such as forward, future, option, swaption, swap, warrant, and other. 
    - NET_REALIZED_GAIN_MON1:
        Net realized gain (loss) attributable to derivatives for the first month of the reporting period.
    - NET_UNREALIZED_AP_MON1:
        Net change in unrealized appreciation (or depreciation) attributable to derivatives for the first month.
    - NET_REALIZED_GAIN_MON2: 
        Net realized gain (loss) attributable to derivatives for the second month of the reporting period.
    - NET_UNREALIZED_AP_MON2:
         Net change in unrealized appreciation (or depreciation) attributable to derivatives for the second month.
    - NET_REALIZED_GAIN_MON3:
        Net realized gain (loss) attributable to derivatives for the third month of the reporting period.
    - NET_UNREALIZED_AP_MON3:
        Net change in unrealized appreciation (or depreciation) attributable to derivatives for the third month.

Table: FUND_VAR_INFO 
    - This table provides information about the Fund's designated index.
    - ACCESSION_NUMBER (Primary Key): 
        This is a 20-character identifier that is unique to every document 
        submitted to the SEC (Securities and Exchange Commission) through the EDGAR system. 
        The first 10 digits represent the entity making the filing, 
        followed by the filing year (24 for 2024), and the sequence of the filing.
        This unique number allows users and regulators to track this specific report.
    - DESIGNATED_INDEX_NAME: 
        Name of the designated index associated with the fund, particularly for those funds subject to the Relative Value at Risk (VaR) Test during the reporting period. 
        If the fund's designated reference portfolio is its securities portfolio, this field may instead contain a statement indicating that. 
    - DESIGNATED_INDEX_IDENTIFIER: 
        The identifier for the fund's designated index, which may be a specific code or alphanumeric string 
        used to uniquely identify the index in financial databases.

Table: FUND_REPORTED_HOLDING 
    - This table contains information about the holdings of the fund, including key identifiers, financial metrics, and contextual information about issuers and assets.
    -  ACCESSION_NUMBER (Primary Key):
        This is a 20-character identifier that is unique to every document 
        submitted to the SEC (Securities and Exchange Commission) through the EDGAR system. 
        The first 10 digits represent the entity making the filing, 
        followed by the filing year (24 for 2024), and the sequence of the filing.
        This unique number allows users and regulators to track this specific report.
    -  HOLDING_ID (Primary Key):
        A surrogate key that uniquely identifies each holding in the fund's portfolio. 
    -  ISSUER_NAME:
        The name of the entity that issued the security or investment held by the fund.
    -  ISSUER_LEI:
        The Legal Entity Identifier (LEI) of the issuer, if available. For holdings in a fund that is a series of a series trust, this should reflect the LEI of the specific series.
    -  ISSUER_TITLE:
        The title of the issue or a description of the investment, providing additional context regarding the specific security held.
    -  ISSUER_CUSIP:
        The Committee on Uniform Securities Identification Procedures (CUSIP) number assigned to the security, which uniquely identifies it in the financial markets.
    -  BALANCE:
        The balance or amount held of the security, expressed in a numerical format. This reflects how much of the investment is currently owned by the fund.
    -  UNIT:
        Indicates the unit of measurement for the balance amount, such as shares, principal amount, or other units. It helps clarify how the balance is quantified.
    -  CURRENCY_CODE:
        The code representing the currency in which the balance is reported (e.g., USD for U.S. dollars, EUR for euros).
    -  CURRENCY_VALUE:
        The total value of the holding expressed in the specified currency.
    -  PERCENTAGE:
        The percentage value of the holding compared to the net assets of the fund, providing insights into how significant the holding is relative to the fund's overall portfolio.
    -  PAYOFF_PROFILE:
        Indicates the payoff profile of the investment, categorizing it as long, short, or not applicable (N/A).
    -  ASSET_CAT:
        Categorizes the asset type of the holding.
    -  ISSUER_TYPE:
        Indicates the type of issuer of the security, providing context for the holding's risk profile.
    -  INVESTMENT_COUNTRY:
        Reports the ISO country code corresponding to the country where the issuer is organized. This is important for understanding geographic exposure.
    -  IS_RESTRICTED_SECURITY:
        A flag indicating whether the investment is classified as a restricted security.
    -  FAIR_VALUE_LEVEL:
        Indicates the level within the fair value hierarchy as defined by US GAAP, which classifies fair value measurements based on the observability of inputs used in the valuation.

Table: IDENTIFIERS
    - This table contains other identifiers for the holding, ensuring comprehensive tracking and cross-referencing of securities.
    - HOLDING_ID (Primary Key):
        A surrogate key that uniquely identifies each holding in the fund's portfolio. 
    - IDENTIFIERS_ID (Primary Key):
        A surrogate key that uniquely identifies each record within the identifiers table. 
    - IDENTIFIER_ISIN:
        The International Securities Identification Number (ISIN) assigned to the security.
    - IDENTIFIER_TICKER:
        The ticker symbol for the security, which is a unique series of letters used to represent the security on stock exchanges.
    - OTHER_IDENTIFIER:
        Additional identifiers associated with the holding that are not covered by the ISIN or ticker.
    - OTHER_IDENTIFIER_DESC:
        A description of the type of other identifier used in the OTHER_IDENTIFIER field.

Table: DEBT_SECURITY
    - This table contains additional information for debt securities holdings, including metrics such as maturity dates, coupon types, and any default statuses.
    - HOLDING_ID:
        A surrogate key that uniquely identifies each holding in the fund's portfolio. 
    - MATURITY_DATE:
        The date on which the debt security is scheduled to mature, e.g. the date when the issuer must repay the principal amount to the holder.
    - COUPON_TYPE:
        Categorizes the coupon type of the debt security. The categories include fixed, floating, variable, or none.
    - ANNUALIZED_RATE:
        The annualized interest rate of the debt security, which provides essential information about the expected return from the security over a year.
    - IS_DEFAULT:
        A flag indicating whether the debt security is currently in default. This is a critical risk indicator, as default can affect the recoverability of the principal and interest payments.
    - ARE_ANY_INTEREST_PAYMENT:
        A flag indicating whether there are any interest payments that are in arrears or have any coupon payments that have been legally deferred by the issuer.
    - IS_ANY_PORTION_INTEREST_PAID:
        A flag indicating whether any portion of the interest on the debt security has been paid in kind (PIK). PIK interest is paid in the form of additional securities rather than cash.
    - IS_CONVTIBLE_MANDATORY:
        A flag indicating whether the debt security is a mandatory convertible security. 
    - IS_CONVTIBLE_CONTINGENT:
        A flag indicating whether the debt security is a contingent convertible security.

Table: DEBT_SECURITY_REF_INSTRUMENT
    - This table contains information about each debt security reference instrument within a portfolio, including identifiers, issuer details, and currency information.
    - HOLDING_ID (Primary Key):
        This is a unique identifier for each holding in the schedule of portfolio investments. It links the debt security reference instrument to a specific holding.
    - DEBT_SECURITY_REF_ID:
        A surrogate key that uniquely identifies each debt security reference instrument entry within this table.
    - ISSUER_NAME:
        The official name of the entity or organization that issued the debt security. This field provides the name for identification and reference.
    - ISSUE_TITLE:
        The title or descriptive name of the debt security issue, indicating the type or series of the security.
    - CURRENCY_CODE:
        The 3-character code representing the currency in which the security is denominated.
    - CUSIP:
        A 9-character identifier assigned to the debt security in the United States.
    - ISIN:
        The 12-character International Securities Identification Number, a globally recognized code for uniquely identifying securities.
    - TICKER:
        The ticker symbol associated with the debt security.
    - OTHER_IDENTIFIER:
        An additional identifier for the debt security if one is available, providing an alternative means of identification beyond CUSIP or ISIN.
    - OTHER_DESC:
        A description of the type of identifier provided in the OTHER_IDENTIFIER field, specifying the kind of alternative identifier being used.

Table: CONVERTIBLE_SECURITY_CURRENCY
    - This table contains information about convertible securities, including identifiers, conversion ratio, and currency information associated with each security.
    - HOLDING_ID (Primary Key):
        This is a unique identifier for each holding in the schedule of portfolio investments, linking the convertible security to a specific holding.
    - CONVERTIBLE_SECURITY_ID:
        A surrogate key that uniquely identifies each convertible security entry within this table.
    - CONVERSION_RATIO:
        The conversion ratio for the convertible security, indicating the rate at which the security can be converted into another form.
    - CURRENCY_CODE:
        The 3-character code representing the currency associated with the convertible security.

Table: REPURCHASE_AGREEMENT
    - This table contains information about repurchase agreements, including transaction type, clearing details, counterparty information, repurchase rate, and maturity date.
    - HOLDING_ID (Primary Key):
        This is a unique identifier for each holding in the schedule of portfolio investments, linking the repurchase agreement to a specific holding.
    - TRANSACTION_TYPE:
        The category that most closely describes the type of transaction, indicating whether it is a repurchase or reverse repurchase agreement.
    - IS_CLEARED:
        Indicates whether the transaction is cleared by a central counterparty, with a designation of "Y" for cleared and "N" for not cleared.
    - CENTRAL_COUNTER_PARTY:
        The name of the central counterparty responsible for clearing the transaction, if applicable.
    - IS_TRIPARTY:
        Specifies if the transaction is a tri-party agreement, where a third party is involved in managing the collateral, with a designation of "Y" for yes and "N" for no.
    - REPURCHASE_RATE:
        The repurchase rate applied to the agreement, representing the interest rate or return rate associated with the transaction.
    - MATURITY_DATE:
        The maturity date of the repurchase agreement, indicating when the agreement is set to conclude.

Table: REPURCHASE_COUNTERPARTY
    - This table contains information about the counterparties involved in repurchase agreements, including unique identifiers, counterparty names, and LEI information.
    - HOLDING_ID (Primary Key):
        This is a unique identifier for each holding in the schedule of portfolio investments, linking the repurchase counterparty information to a specific holding.
    - REPURCHASE_COUNTERPARTY_ID:
        A surrogate key that uniquely identifies each counterparty entry within this table.
    - NAME:
        The name of the counterparty involved in the repurchase agreement, identifying the organization or entity responsible for the counterparty role.
    - LEI:
        The Legal Entity Identifier (LEI) of the counterparty, if available. This is a 20-character alphanumeric code used globally to identify legal entities in financial transactions.

Table: REPURCHASE_COLLATERAL
    This table contains information about the collateral associated with repurchase agreements, including principal and collateral amounts, currency codes, investment categories, and descriptions.
    - HOLDING_ID (Primary Key):
        This is a unique identifier for each holding in the schedule of portfolio investments, linking the repurchase collateral information to a specific holding.
    - REPURCHASE_COLLATERAL_ID:
        A surrogate key that identifies each collateral entry within this table.
    - PRINCIPAL_AMOUNT:
        The principal amount of the repurchase agreement, representing the initial amount provided in the transaction.
    - PRINCIPAL_CURRENCY_CODE:
        The 3-character currency code associated with the principal amount, indicating the currency in which the principal is denominated.
    - COLLATERAL_AMOUNT:
        The value of the collateral provided in the repurchase agreement, representing the worth of assets pledged as security.
    - COLLATERAL_CURRENCY_CODE:
        The 3-character currency code associated with the collateral amount, indicating the currency in which the collateral is valued.
    - INVESTMENT_CAT:
        The category of investments that most closely represents the type of collateral provided, such as specific asset classes.
    - OTHER_INSTRUMENT_DESC:
        A brief description provided if the category of the investment is designated as "Other Instrument," giving context about the collateral.

Table: DERIVATIVE_COUNTERPARTY
    - This table contains information about the counterparties involved in derivative transactions, including unique identifiers, counterparty names, and LEI information.
    - HOLDING_ID (Primary Key):
        This is a unique identifier for each holding in the schedule of portfolio investments, linking the derivative counterparty information to a specific holding.
    - DERIVATIVE_COUNTERPARTY_ID:
        A surrogate key that uniquely identifies each derivative counterparty entry within this table.
    - DERIVATIVE_COUNTERPARTY_NAME:
        The name of the counterparty involved in the derivative transaction, identifying the organization or entity responsible for the counterparty role.
    - DERIVATIVE_COUNTERPARTY_LEI:
        The Legal Entity Identifier (LEI) of the counterparty, if available. This is a 20-character alphanumeric code used globally to identify legal entities in financial transactions.

Table: SWAPTION_OPTION_WARNT_DERIV
    - This table contains information about options and warrants, including attributes such as the type of option, payoff profile, and underlying share counts.
    - HOLDING_ID (Primary Key):
        This is a unique identifier for each holding in the schedule of portfolio investments, linking the derivative counterparty information to a specific holding.
    - PUT_OR_CALL:
        Indicates if the option is a "put" or "call."
    - WRITTEN_OR_PURCHASED: 
        Specifies if the option was "written" or "purchased."
    - SHARES_CNT:
        The number of shares of the underlying instrument per contract.
    - PRINCIPAL_AMOUNT:
        Represents the principal amount of the underlying reference instrument per contract. 
    - CURRENCY_CODE:
        The currency code for the contract.
    - EXERCISE_PRICE:
        Specifies the exercise price or rate for the contract. 
    - EXPIRATION_DATE:
        The expiration date of the contract. 
    - UNREALIZED_APPRECIATION:
        Indicates unrealized appreciation or depreciation of the instrument. Depreciation is reported as a negative value. 

Table: DESC_REF_INDEX_BASKET
    - This table contains the index or custom basket reference instrument for options and warrants, including options on a derivative (swaptions).
    - HOLDING_ID (Primary Key):
        This is a unique identifier for each holding in the schedule of portfolio investments, linking the derivative counterparty information to a specific holding.
    - INDEX_NAME:
        Specifies the name of the index associated with the holding. 
    - INDEX_IDENTIFIER:
        Provides a unique identifier for the index. 
    - NARRATIVE_DESC:
        Contains a narrative description of the index. 

Table: DESC_REF_INDEX_COMPONENT
    - This table provides detailed information on individual components within index references associated with portfolio holdings.
    - HOLDING_ID (Primary Key):
        This is a unique identifier for each holding in the schedule of portfolio investments, linking the derivative counterparty information to a specific holding.
    - DESC_REF_INDEX_COMPONENT_ID:
        A unique surrogate key for each component within an index reference. 
    - NAME:
        The name of the index component. 
    - CUSIP:
        The CUSIP identifier for the component, used for U.S.-based securities. 
    - ISIN:
        The ISIN (International Securities Identification Number) for the component. 
    - TICKER:
        The stock ticker symbol for the component. 
    - OTHER_IDENTIFIER:
        Another identifier for the component if CUSIP or ISIN are not applicable.
    - OTHER_DESC:
        The type of the alternative identifier used. 
    - NOTIONAL_AMOUNT:
        The notional amount for the component in the index. 
    - CURRENCY_CODE:
        The currency code in which the notional amount is denominated. 
    - VALUE:
        The current value of the component. 
    - ISSUER_CURRENCY_CODE:
        The currency code of the issuer for the component. 

Table: DESC_REF_OTHER 
    - This table stores information about other descriptive references associated with portfolio holdings.
    - HOLDING_ID (Primary Key):
        This is a unique identifier for each holding in the schedule of portfolio investments, linking the derivative counterparty information to a specific holding.
    - DESC_REF_OTHER_ID:
        A unique surrogate key for each other reference. 
    - ISSUER_NAME:
        The name of the issuer for the referenced instrument. 
    - ISSUE_TITLE:
        The title or designation of the issue by the issuer. 
    - CUSIP:
        The CUSIP identifier for the instrument, specific to U.S. securities. 
    - ISIN:
        The ISIN (International Securities Identification Number) for the instrument. 
    - TICKER:
        The stock ticker symbol for the instrument. 
    - OTHER_IDENTIFIER:
        Another identifier if CUSIP or ISIN are not applicable. 
    - OTHER_DESC:
        Describes the type of alternative identifier used. 

Table: FUT_FWD_NONFOREIGNCUR_CONTRA
    - This table contains information about futures and forward contracts not denominated in foreign currency. 
    - HOLDING_ID (Primary Key):
        This is a unique identifier for each holding in the schedule of portfolio investments, linking the derivative counterparty information to a specific holding.
    - PAYOFF_PROFILE:
        Indicates the payoff profile of the contract, selected as either "long" or "short." 
    - EXPIRATION_DATE:
        The expiration date of the contract. 
    - NOTIONAL_AMOUNT:
        Represents the aggregate notional amount or contract value on the trade date. 
    - CURRENCY_CODE:
        The currency code in which the contract is denominated. 
    - UNREALIZED_APPRECIATION:
        Indicates the unrealized appreciation or depreciation of the contract, with depreciation recorded as a negative value. 

Table: FWD_FOREIGNCUR_CONTRACT_SWAP
    - This table contains information about forward contracts and currency swaps involving foreign currencies. 
    - HOLDING_ID (Primary Key):
        This is a unique identifier for each holding in the schedule of portfolio investments, linking the derivative counterparty information to a specific holding.
    - CURRENCY_SOLD_AMOUNT: 
        The amount of currency sold in the contract. 
    - DESC_CURRENCY_SOLD:
        A description or code for the currency sold. 
    - CURRENCY_PURCHASED_AMOUNT:
        The amount of currency purchased in the contract.
    - DESC_CURRENCY_PURCHASED:
        A description or code for the currency purchased. 
    - SETTLEMENT_DATE:
        The date when the contract is set to settle. 
    - UNREALIZED_APPRECIATION: 
        The unrealized appreciation or depreciation of the contract, with depreciation reported as a negative number. 

Table: NONFOREIGN_EXCHANGE_SWAP
    - This table contains swap information (other than foreign exchange swaps).
    - HOLDING_ID (Primary Key):
        This is a unique identifier for each holding in the schedule of portfolio investments, linking the derivative counterparty information to a specific holding.
    - SWAP_FLAG: 
        An indicator of whether this is a custom or standard swap. This flag differentiates customized swaps from standardized market swaps.
    - TERMINATION_DATE: 
        The date on which the swap agreement ends, marking the maturity or close of the swap transaction.
    - UPFRONT_PAYMENT: 
        The amount paid upfront to initiate the swap. Upfront payments are often made for certain types of swaps as an initial commitment.
    - PMNT_CURRENCY_CODE: 
        The currency in which the upfront payment is made, represented by a currency code.
    - UPFRONT_RECEIPT: 
        Any amount received upfront in connection with the swap, recorded separately from the payment.
    - RCPT_CURRENCY_CODE: 
        The currency in which the upfront receipt is received.
    - NOTIONAL_AMOUNT: 
        The notional or face amount on which the swap payments are based, which represents the principal underlying the swap.
    - CURRENCY_CODE: 
        The currency in which the notional amount is denominated.
    - UNREALIZED_APPRECIATION: 
        The unrealized appreciation or depreciation of the swap's market value, reported as a positive or negative number, depending on gains or losses.
    - FIXED_OR_FLOATING_RECEIPT: 
        Indicates whether the swap involves a fixed, floating, or other type of receipt.
    - FLOATING_RATE_INDEX_RECEIPT: 
        The floating rate index used if the receipt is floating.
    - FLOATING_RATE_SPREAD_RECEIPT: 
        The spread added to the floating rate index to determine the interest rate for the receipt.
    - CURRENCY_CODE_RECEIPT: 
        The currency of the receipt, showing the denomination of payments received.
    - AMOUNT_RECEIPT: 
        The actual amount received in the swap transaction based on the terms.
    - FIXED_OR_FLOATING_PAYMENT: 
        Specifies if the payment under the swap is fixed, floating, or follows another type.
    - FIXED_RATE_PAYMENT: 
        The fixed rate applied to payments if the swap involves fixed payments.
    - CURRENCY_CODE_PAYMENT: 
        The currency of the payment, indicating the denomination.
    - AMOUNT_PAYMENT: 
        The payment amount calculated based on the swap terms, including any fixed or floating rates.

Table: FLOATING_RATE_RESET_TENOR
    - This table is for swaps, the terms of payments paid and received.
    - HOLDING_ID (Dual Primary Key):
        This is a unique identifier for each holding in the schedule of portfolio investments, linking the derivative counterparty information to a specific holding.
    - RATE_RESET_TENOR_ID (Dual Primary Key): 
        A surrogate key that uniquely identifies each reset tenor entry within the swap.
    - RECEIPT_OR_PAYMENT: 
        This column specifies whether the entry is related to a receipt or payment under the swap. 
        This distinction helps identify the direction of cash flows in the swap.
    - RESET_DATE: 
        The scheduled date for resetting the floating interest rate. This periodic reset adjusts the floating rate based on current market conditions.
    - RESET_DATE_UNIT: 
        Specifies the unit for the reset frequency, such as days or months, providing context for how often the rate adjusts.
    - RATE_TENOR: 
        The term or period used to calculate the interest rate for the reset. This term can influence the rate applied to each reset period.
    - RATE_TENOR_UNIT: 
        Specifies the unit for the rate tenor, such as days or months, indicating the length of the period over which the interest rate is calculated.

Table: OTHER_DERIV
    - This table contains information for other derivatives.
    - HOLDING_ID (Primary Key):
        This is a unique identifier for each holding in the schedule of portfolio investments, linking the derivative counterparty information to a specific holding.
    - OTHER_DESC: 
        A brief description of the derivative instrument, explaining its nature if it does not fall under conventional categories.
    - TERMINATION_DATE: 
        The termination or maturity date of the derivative, marking the end of the contract.
    - UNREALIZED_APPRECIATION: 
        The unrealized appreciation or depreciation of the derivative, reflecting market value changes since the acquisition.

Table: OTHER_DERIV_NOTIONAL_AMOUNT
    - This table contains notional amount(s) for other derivatives.
    - HOLDING_ID (Dual Primary Key):
        This is a unique identifier for each holding in the schedule of portfolio investments, linking the derivative counterparty information to a specific holding.
    - OTHER_DERIV_NOTIONAL_AMOUNT_ID (Dual Primary Key): 
        A surrogate key uniquely identifying each notional amount entry for “Other Derivative” instruments.
    - NOTIONAL_AMOUNT: 
        The face or notional amount of the derivative, serving as the reference amount for payment calculations.
    - CURRENCY_CODE: 
        The currency code representing the currency in which the notional amount is denominated.

Table: SECURITIES_LENDING
    - This table contains information for securities lending.
    - HOLDING_ID (Primary Key):
        This is a unique identifier for each holding in the schedule of portfolio investments, linking the derivative counterparty information to a specific holding.
    - IS_CASH_COLLATERAL: 
        A flag indicating whether cash collateral was received for the loaned securities. 
        If set to “yes” (Y), cash was received; otherwise, another form of collateral was provided.
    - IS_NON_CASH_COLLATERAL: 
        A flag indicating whether any portion of the collateral received was non-cash, such as securities or other assets.
    - IS_LOAN_BY_FUND: 
        A flag indicating whether the fund itself is the lender of the securities. This shows if the fund is directly engaging in securities lending.

Table: EXPLANATORY_NOTE
    - This table contains any information provided by the fund in response to an item.
    - ACCESSION_NUMBER (Dual Primary Key): 
        This is a 20-character identifier that is unique to every document 
        submitted to the SEC (Securities and Exchange Commission) through the EDGAR system. 
        The first 10 digits represent the entity making the filing, 
        followed by the filing year (24 for 2024), and the sequence of the filing.
        This unique number allows users and regulators to track this specific report.
    - EXPLANATORY_NOTE_ID (Dual Primary Key): 
        This is a surrogate key that uniquely identifies each explanatory note entry within a single filing.
    - ITEM_NO: 
        This column indicates the specific item number from the filing form to which the explanatory note refers. 
        Item numbers help pinpoint the section or data field that the note is clarifying or expanding upon, providing users with precise context.
    - EXPLANATORY_NOTE: 
        This is a text field that contains the actual explanatory note. It can include any remarks, descriptions, or additional information that 
        the fund managers or preparers deem necessary for clarifying specific aspects of the filing. This could involve explanations about unusual transactions, 
        assumptions used in valuations, or other notable details that impact how data in the filing should be interpreted.
```
"""

# Instructions for handling parts of the natural language query
nlp_query_handling_instructions = """
```
Natural Language Processing Instructions:
- Decompose the user's query to identify requirements regarding asset classes, sectors, time periods, or specific filings.
- Detect keywords related to filing dates, submission types, registrant details, and financial data.
```
"""

# Define default behavior for unspecified fields or conditions
default_query_behavior = f"""
```
Default assumptions:
- Include all asset classes and sectors unless specified in the question
- Retrieve all rows if no specific criteria are provided, only use LIMIT clauses when the question asks for the "highest", "most", "best", or "largest" of something.
- Do not use ORDER BY unless specified in the question.
- Do not use arithmetic or aggregate functions unless specified in the question.
- When using arithmetics or aggregate functions, type cast columns from TEXT to FLOAT before computation. 
- Always use common table expressions instead of using nested queries or calculating values within SELECT statements when possible.
- Do not rename columns or use aliases in the output unless specified in the question
```
"""

# Example Natural Language Queries and Corresponding SQL Translations
example_queries = """
```
Example queries set, where Natural language request is encased in double quotations " and desired output is the SQL query after 'SQL:'
1. "List the top 5 registrants by total net assets, including their CIK and country."
   SQL: 
   WITH FundAssets AS (
       SELECT R.CIK, R.REGISTRANT_NAME, R.COUNTRY, F.NET_ASSETS
       FROM REGISTRANT R
       JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
   )
   SELECT CIK, REGISTRANT_NAME, COUNTRY, NET_ASSETS
   FROM FundAssets
   ORDER BY NET_ASSETS DESC
   LIMIT 5;

2. "Calculate the collateral amount for repurchase agreements grouped by counterparty."
   SQL: 
   WITH CollateralCTE AS (
    SELECT RCP.NAME AS Counterparty_Name, SUM(RC.COLLATERAL_AMOUNT) AS Total_Collateral
    FROM REPURCHASE_COLLATERAL RC
    JOIN REPURCHASE_COUNTERPARTY RCP ON RC.HOLDING_ID = RCP.HOLDING_ID
    GROUP BY RCP.NAME
   )
   SELECT Counterparty_Name, Total_Collateral
   FROM CollateralCTE
   ORDER BY Total_Collateral DESC;

3. "Find funds that have both securities lending activities and repurchase agreements."
   SQL: 
   WITH SecuritiesLending AS (
       SELECT ACCESSION_NUMBER
       FROM SECURITIES_LENDING
       WHERE IS_LOAN_BY_FUND = 'Y'
   ),
   RepurchaseAgreements AS (
       SELECT ACCESSION_NUMBER
       FROM REPURCHASE_AGREEMENT
   )
   SELECT F.SERIES_NAME
   FROM FUND_REPORTED_INFO F
   WHERE F.ACCESSION_NUMBER IN (SELECT ACCESSION_NUMBER FROM SecuritiesLending)
     AND F.ACCESSION_NUMBER IN (SELECT ACCESSION_NUMBER FROM RepurchaseAgreements);

4. "Find borrowers who have borrowed more than $5,000,000, including their names and LEIs."
   SQL: 
   WITH BorrowedAmounts AS (
       SELECT BORROWER_ID, SUM(AGGREGATE_VALUE) AS Total_Borrowed
       FROM BORROWER
       GROUP BY BORROWER_ID
       HAVING SUM(AGGREGATE_VALUE) > 5000000
   )
   SELECT B.NAME, B.LEI, BA.Total_Borrowed
   FROM BORROWER B
   JOIN BorrowedAmounts BA ON B.BORROWER_ID = BA.BORROWER_ID;

5. "Calculate the average annualized rate for debt securities grouped by coupon."
   SQL: 
   WITH RateAverages AS (
       SELECT DS.COUPON_TYPE, AVG(DS.ANNUALIZED_RATE) AS Avg_Annualized_Rate
       FROM DEBT_SECURITY DS
       WHERE DS.ANNUALIZED_RATE IS NOT NULL
       GROUP BY DS.COUPON_TYPE
   )
   SELECT COUPON_TYPE, Avg_Annualized_Rate
   FROM RateAverages
   ORDER BY Avg_Annualized_Rate DESC;

6. "Find funds that have experienced a net decrease in assets over the last three reporting periods."
   SQL: 
   WITH AssetChanges AS (
       SELECT F.ACCESSION_NUMBER, F.SERIES_NAME, S.REPORT_DATE, F.NET_ASSETS,
              LAG(F.NET_ASSETS, 1) OVER (PARTITION BY F.SERIES_NAME ORDER BY S.REPORT_DATE) AS Previous_Period_Assets
       FROM FUND_REPORTED_INFO F
       JOIN SUBMISSION S ON F.ACCESSION_NUMBER = S.ACCESSION_NUMBER
   )
   SELECT DISTINCT AC.SERIES_NAME
   FROM AssetChanges AC
   WHERE AC.NET_ASSETS < AC.Previous_Period_Assets
     AND AC.Previous_Period_Assets IS NOT NULL;

7. "Identify issuers with more than three different securities holdings, include their names and CUSIPs."
   SQL: 
   WITH IssuerHoldings AS (
       SELECT H.ISSUER_NAME, H.ISSUER_CUSIP, COUNT(DISTINCT H.HOLDING_ID) AS Holding_Count
       FROM FUND_REPORTED_HOLDING H
       GROUP BY H.ISSUER_NAME, H.ISSUER_CUSIP
       HAVING COUNT(DISTINCT H.HOLDING_ID) > 3
   )
   SELECT ISSUER_NAME, ISSUER_CUSIP, Holding_Count
   FROM IssuerHoldings
   ORDER BY Holding_Count DESC;

8. "Calculate the total notional amount of derivatives per currency and return the top 3 currencies by notional amount."
    SQL: 
    WITH NotionalSums AS (
        SELECT ODNA.CURRENCY_CODE, SUM(ODNA.NOTIONAL_AMOUNT) AS Total_Notional
        FROM OTHER_DERIV_NOTIONAL_AMOUNT ODNA
        GROUP BY ODNA.CURRENCY_CODE
    )
    SELECT CURRENCY_CODE, Total_Notional
    FROM NotionalSums
    ORDER BY Total_Notional DESC
    LIMIT 3;

9. "Get the funds with liquidation preferences greater than their net assets."
    SQL: 
    WITH FundPreferences AS (
        SELECT F.SERIES_NAME, F.LIQUIDATION_PREFERENCE, F.NET_ASSETS
        FROM FUND_REPORTED_INFO F
    )
    SELECT SERIES_NAME, LIQUIDATION_PREFERENCE, NET_ASSETS
    FROM FundPreferences
    WHERE LIQUIDATION_PREFERENCE > NET_ASSETS;

10. "Find all convertible securities that are contingent and have a conversion ratio above 1.5."
    SQL: 
    WITH ConvertibleCTE AS (
        SELECT DS.HOLDING_ID, CSC.CONVERSION_RATIO
        FROM DEBT_SECURITY DS
        JOIN CONVERTIBLE_SECURITY_CURRENCY CSC ON DS.HOLDING_ID = CSC.HOLDING_ID
        WHERE DS.IS_CONVTIBLE_CONTINGENT = 'Y' AND CSC.CONVERSION_RATIO > 1.5
    )
    SELECT HOLDING_ID, CONVERSION_RATIO
    FROM ConvertibleCTE;

11. "Find the total unrealized appreciation for each asset category for all funds."
    SQL: 
    WITH AppreciationCTE AS (
        SELECT H.ASSET_CAT, SUM(H.PERCENTAGE * H.CURRENCY_VALUE) AS Total_Unrealized_App
        FROM FUND_REPORTED_HOLDING H
        GROUP BY H.ASSET_CAT
    )
    SELECT ASSET_CAT, Total_Unrealized_App
    FROM AppreciationCTE
    ORDER BY Total_Unrealized_App DESC;

12. "Analyze the distribution of asset categories for the top 10 largest funds by their total assets."
    SQL: 
    WITH TopFunds AS (
        SELECT SERIES_NAME, ACCESSION_NUMBER
        FROM FUND_REPORTED_INFO
        ORDER BY TOTAL_ASSETS DESC
        LIMIT 10
    ),
    AssetDistribution AS (
        SELECT H.ASSET_CAT, COUNT(*) AS Category_Count
        FROM FUND_REPORTED_HOLDING H
        JOIN TopFunds T ON H.ACCESSION_NUMBER = T.ACCESSION_NUMBER
        GROUP BY H.ASSET_CAT
    )
    SELECT ASSET_CAT, Category_Count
    FROM AssetDistribution
    ORDER BY Category_Count DESC;

14. "Compare the latest net assets of the top 5 funds."
   SQL: 
   WITH TopPerformingFunds AS (
    SELECT 
        ACCESSION_NUMBER, 
        (MONTHLY_TOTAL_RETURN1 + MONTHLY_TOTAL_RETURN2 + MONTHLY_TOTAL_RETURN3) / 3.0 AS Avg_Return
    FROM 
        MONTHLY_TOTAL_RETURN
    ORDER BY 
        Avg_Return DESC
    LIMIT 5
   )
   SELECT 
      FR.SERIES_NAME, 
      FR.NET_ASSETS, 
      TP.Avg_Return
   FROM 
      TopPerformingFunds TP
   JOIN 
      FUND_REPORTED_INFO FR ON TP.ACCESSION_NUMBER = FR.ACCESSION_NUMBER;

15. "Calculate the average return across all funds for the most recent month."
   SQL: 
   WITH LatestReturns AS (
    SELECT 
        M.ACCESSION_NUMBER, 
        M.MONTHLY_TOTAL_RETURN1
    FROM 
        MONTHLY_TOTAL_RETURN M
    JOIN 
        SUBMISSION S ON M.ACCESSION_NUMBER = S.ACCESSION_NUMBER
    WHERE 
        S.REPORT_DATE = (SELECT MAX(REPORT_DATE) FROM SUBMISSION)
   )
   SELECT 
      AVG(MONTHLY_TOTAL_RETURN1) AS Average_Return
   FROM 
      LatestReturns;

16. "Find the interest rate risk for each fund and give me those with the highest risk scores."
   SQL: 
   WITH InterestRiskScores AS (
    SELECT 
        IR.ACCESSION_NUMBER, 
        -- Calculating composite risk score by summing absolute values of DV01 and DV100 columns
        (ABS(CAST(IR.INTRST_RATE_CHANGE_3MON_DV01 AS FLOAT)) +
         ABS(CAST(IR.INTRST_RATE_CHANGE_1YR_DV01 AS FLOAT)) +
         ABS(CAST(IR.INTRST_RATE_CHANGE_5YR_DV01 AS FLOAT)) +
         ABS(CAST(IR.INTRST_RATE_CHANGE_10YR_DV01 AS FLOAT)) +
         ABS(CAST(IR.INTRST_RATE_CHANGE_30YR_DV01 AS FLOAT)) +
         ABS(CAST(IR.INTRST_RATE_CHANGE_3MON_DV100 AS FLOAT)) +
         ABS(CAST(IR.INTRST_RATE_CHANGE_1YR_DV100 AS FLOAT)) +
         ABS(CAST(IR.INTRST_RATE_CHANGE_5YR_DV100 AS FLOAT)) +
         ABS(CAST(IR.INTRST_RATE_CHANGE_10YR_DV100 AS FLOAT)) +
         ABS(CAST(IR.INTRST_RATE_CHANGE_30YR_DV100 AS FLOAT))
        ) AS Composite_Risk_Score
    FROM 
        INTEREST_RATE_RISK IR
   )
   SELECT 
      FR.SERIES_NAME, 
      FR.ACCESSION_NUMBER, 
      IRS.Composite_Risk_Score
   FROM 
      InterestRiskScores IRS
   JOIN 
      FUND_REPORTED_INFO FR ON IRS.ACCESSION_NUMBER = FR.ACCESSION_NUMBER
   ORDER BY 
      IRS.Composite_Risk_Score DESC
   LIMIT 5;

17. "Return funds that have experienced a decrease in assets over the last three reporting periods."
   SQL: 
   WITH AssetChanges AS (
       SELECT F.ACCESSION_NUMBER, F.SERIES_NAME, S.REPORT_DATE, F.NET_ASSETS,
              LAG(F.NET_ASSETS, 1) OVER (PARTITION BY F.SERIES_NAME ORDER BY S.REPORT_DATE) AS Previous_Period_Assets
       FROM FUND_REPORTED_INFO F
       JOIN SUBMISSION S ON F.ACCESSION_NUMBER = S.ACCESSION_NUMBER
   )
   SELECT DISTINCT AC.SERIES_NAME
   FROM AssetChanges AC
   WHERE AC.NET_ASSETS < AC.Previous_Period_Assets
     AND AC.Previous_Period_Assets IS NOT NULL;

18. "Analyze the composition of fund portfolios by categorizing assets and their total values."
   SQL: 
   WITH PortfolioComposition AS (
    SELECT 
        ACCESSION_NUMBER, 
        ASSET_CAT, 
        SUM(CAST(CURRENCY_VALUE AS FLOAT)) AS Total_Value
    FROM 
        FUND_REPORTED_HOLDING
    GROUP BY 
        ACCESSION_NUMBER, 
        ASSET_CAT
)
SELECT 
    F.SERIES_NAME, 
    PC.ASSET_CAT, 
    PC.Total_Value
FROM 
    PortfolioComposition PC
JOIN 
    FUND_REPORTED_INFO F ON PC.ACCESSION_NUMBER = F.ACCESSION_NUMBER
ORDER BY 
    F.SERIES_NAME, 
    PC.Total_Value DESC;

19. "Find the most common asset categories for all fund portfolios."
    SQL: 
    WITH AssetCounts AS (
        SELECT ASSET_CAT, COUNT(*) AS Count
        FROM FUND_REPORTED_HOLDING
        GROUP BY ASSET_CAT
    )
    SELECT ASSET_CAT, Count
    FROM AssetCounts
    ORDER BY Count DESC
    LIMIT 5;

20. "Determine the percentage of each asset category within individual funds."
    SQL: 
    WITH TotalAssets AS (
    SELECT 
        ACCESSION_NUMBER, 
        SUM(CAST(CURRENCY_VALUE AS FLOAT)) AS Total_Value
    FROM 
        FUND_REPORTED_HOLDING
    GROUP BY 
        ACCESSION_NUMBER
),
CategoryAllocation AS (
    SELECT 
        FH.ACCESSION_NUMBER, 
        FH.ASSET_CAT, 
        SUM(CAST(FH.CURRENCY_VALUE AS FLOAT)) AS Category_Value
    FROM 
        FUND_REPORTED_HOLDING FH
    GROUP BY 
        FH.ACCESSION_NUMBER, 
        FH.ASSET_CAT
   )
   SELECT 
      F.SERIES_NAME, 
      CA.ASSET_CAT, 
      (CA.Category_Value * 100.0 / TA.Total_Value) AS Percentage_Allocation
   FROM 
      CategoryAllocation CA
   JOIN 
      TotalAssets TA ON CA.ACCESSION_NUMBER = TA.ACCESSION_NUMBER
   JOIN 
      FUND_REPORTED_INFO F ON CA.ACCESSION_NUMBER = F.ACCESSION_NUMBER
   ORDER BY 
      F.SERIES_NAME, 
      Percentage_Allocation DESC;
```
"""

# Reasoning instructions
reasoning_instruction = """
```
Reasoning Instructions:
1. Reasoning you provide should first focus on why a nested query was chosen or why it wasn't chosen.
2. It should give a query plan on how to solve this question - explain the mapping of the columns to the words in the input question.
3. It should explain each of the clauses and why they are structured the way they are structured. For example, if there is a `GROUP BY`, an explanation should be given as to why it exists.
4. If there's any `SUM()` or any other function used, it should be explained as to why it was required.
```
"""

output_instruction = """
```
Final output:
Format the generated SQL with proper indentation - the columns in the 
(`SELECT` statement should have more indentation than the keyword `SELECT` 
and so on for each SQL clause.)
Output only the SQLite's SQL query syntax, without blank padding on the left or right, any string prefix suffix, or any delimiters ```.
```
"""

gpt_queries_easy = """
```
Example queries set (easy difficulty) that should not require any nested queries or join statements.

1. "Show me the top 20 largest funds by total assets"
SELECT 
    SERIES_NAME,
    TOTAL_ASSETS
FROM 
    FUND_REPORTED_INFO
ORDER BY 
    CAST(TOTAL_ASSETS AS FLOAT) DESC
LIMIT 20;

2. "List all funds with net assets over 1 billion dollars"
SELECT 
    SERIES_NAME,
    NET_ASSETS 
FROM 
    FUND_REPORTED_INFO 
WHERE 
    CAST(NET_ASSETS AS FLOAT) > 1000000000;

3. "Which asset categories have the highest total investment value?"
SELECT 
    ASSET_CAT,
    SUM(CAST(CURRENCY_VALUE AS FLOAT))
FROM 
    FUND_REPORTED_HOLDING
GROUP BY 
    ASSET_CAT
ORDER BY 
    SUM(CAST(CURRENCY_VALUE AS FLOAT)) DESC
LIMIT 1;

4. "Show me the largest bond funds"
SELECT 
    SERIES_NAME,
    TOTAL_ASSETS
FROM 
    FUND_REPORTED_INFO
WHERE 
    SERIES_NAME LIKE '%BOND%'
ORDER BY 
    CAST(TOTAL_ASSETS AS FLOAT) DESC
LIMIT 1;

5. "Show me the phone numbers of all Vanguard registrants"
SELECT 
    REGISTRANT_NAME,
    PHONE 
FROM 
    REGISTRANT 
WHERE 
    REGISTRANT_NAME LIKE '%VANGUARD%';

6. "Which funds have assets between 100M and 500M?"
SELECT 
    SERIES_NAME,
    TOTAL_ASSETS 
FROM 
    FUND_REPORTED_INFO 
WHERE 
    CAST(TOTAL_ASSETS AS FLOAT) BETWEEN 100000000 AND 500000000;

7. "List all registrants and their cities"
SELECT 
    REGISTRANT_NAME,
    CITY
FROM 
    REGISTRANT;

8. "Which funds have total assets equal to net assets?"
SELECT 
    SERIES_NAME 
FROM 
    FUND_REPORTED_INFO 
WHERE 
    TOTAL_ASSETS = NET_ASSETS;

9. "List all funds with 'Income' in their name"
SELECT 
    SERIES_NAME,
    TOTAL_ASSETS 
FROM 
    FUND_REPORTED_INFO 
WHERE 
    SERIES_NAME LIKE '%INCOME%';

10. "Which funds have the highest liabilities to assets ratio?"
SELECT 
    SERIES_NAME,
    CAST(TOTAL_LIABILITIES AS FLOAT) / CAST(TOTAL_ASSETS AS FLOAT)
FROM 
    FUND_REPORTED_INFO
WHERE 
    TOTAL_ASSETS != '0'
ORDER BY 
    CAST(TOTAL_LIABILITIES AS FLOAT) / CAST(TOTAL_ASSETS AS FLOAT) DESC
LIMIT 1;

11. "Show me all funds with 'Growth' in their name"
SELECT 
    SERIES_NAME,
    TOTAL_ASSETS 
FROM 
    FUND_REPORTED_INFO 
WHERE 
    SERIES_NAME LIKE '%GROWTH%';

12. "List the top 10 funds by net assets"
SELECT 
    SERIES_NAME,
    NET_ASSETS 
FROM 
    FUND_REPORTED_INFO 
ORDER BY 
    CAST(NET_ASSETS AS FLOAT) DESC 
LIMIT 10;

13. "Which funds have zero liabilities?"
SELECT 
    SERIES_NAME 
FROM 
    FUND_REPORTED_INFO 
WHERE 
    TOTAL_LIABILITIES = '0' 
    OR TOTAL_LIABILITIES IS NULL;

14. "Which funds have the most cash on hand?"
SELECT 
    SERIES_NAME,
    CASH_NOT_RPTD_IN_C_OR_D
FROM 
    FUND_REPORTED_INFO
WHERE 
    CASH_NOT_RPTD_IN_C_OR_D IS NOT NULL
ORDER BY 
    CAST(CASH_NOT_RPTD_IN_C_OR_D AS FLOAT) DESC
LIMIT 1;

15. "Show me the smallest 5 funds by total assets"
SELECT 
    SERIES_NAME,
    TOTAL_ASSETS 
FROM 
    FUND_REPORTED_INFO 
WHERE 
    TOTAL_ASSETS IS NOT NULL
ORDER BY 
    CAST(TOTAL_ASSETS AS FLOAT) ASC 
LIMIT 5;

16. "Which registrants have multiple phone numbers?"
SELECT 
    REGISTRANT_NAME,
    COUNT(DISTINCT PHONE)
FROM 
    REGISTRANT
GROUP BY 
    REGISTRANT_NAME
HAVING 
    COUNT(DISTINCT PHONE) > 1;

17. "Show me all registrants from Florida"
SELECT 
    REGISTRANT_NAME,
    CITY,
    ADDRESS1 
FROM 
    REGISTRANT 
WHERE 
    STATE = 'FL';

18. "Show me funds with the highest ratio of cash to total assets"
SELECT 
    SERIES_NAME,
    CAST(CASH_NOT_RPTD_IN_C_OR_D AS FLOAT) / CAST(TOTAL_ASSETS AS FLOAT)
FROM 
    FUND_REPORTED_INFO
WHERE 
    CASH_NOT_RPTD_IN_C_OR_D IS NOT NULL 
    AND TOTAL_ASSETS > 0
ORDER BY 
    CAST(CASH_NOT_RPTD_IN_C_OR_D AS FLOAT) / CAST(TOTAL_ASSETS AS FLOAT) DESC
LIMIT 1;

19. "List all funds with 'Index' in their name"
SELECT 
    SERIES_NAME,
    TOTAL_ASSETS 
FROM 
    FUND_REPORTED_INFO 
WHERE 
    SERIES_NAME LIKE '%INDEX%';

20. "List all registrants with their ZIP codes"
SELECT 
    REGISTRANT_NAME,
    ZIP
FROM 
    REGISTRANT;

21."Show me all equity-focused funds"
SELECT 
    SERIES_NAME,
    TOTAL_ASSETS
FROM 
    FUND_REPORTED_INFO
WHERE 
    SERIES_NAME LIKE '%EQUITY%'
    OR SERIES_NAME LIKE '%STOCK%'
ORDER BY 
    CAST(TOTAL_ASSETS AS FLOAT) DESC;

22. "List all registrants with their country"
SELECT 
    REGISTRANT_NAME,
    COUNTRY
FROM 
    REGISTRANT;

23. "I'm looking for any funds with 'sustainable' or 'ESG' in their name what's their total AUM?"
SELECT 
    COUNT(*),
    SUM(CAST(TOTAL_ASSETS AS FLOAT))
FROM 
    FUND_REPORTED_INFO
WHERE 
    SERIES_NAME LIKE '%SUSTAINABLE%'
    OR SERIES_NAME LIKE '%ESG%';

24. "Could you check which states have the most fund registrants? Top 5 is fine."
SELECT 
    STATE,
    COUNT(DISTINCT REGISTRANT_NAME)
FROM 
    REGISTRANT
GROUP BY 
    STATE
ORDER BY 
    COUNT(DISTINCT REGISTRANT_NAME) DESC
LIMIT 5;

25. "Which registrants are based in California?"
SELECT 
    DISTINCT REGISTRANT_NAME
FROM 
    REGISTRANT 
WHERE 
    STATE = 'US-CA';

26. "List all funds with no reported liabilities."
SELECT 
    SERIES_NAME 
FROM 
    FUND_REPORTED_INFO 
WHERE 
    TOTAL_LIABILITIES = '0' 
    OR TOTAL_LIABILITIES IS NULL;

27. "Show me all interest rate risks with a 3-month DV01 value exceeding 1 million"
SELECT 
    ACCESSION_NUMBER,
    INTRST_RATE_CHANGE_3MON_DV01 
FROM 
    INTEREST_RATE_RISK 
WHERE 
    CAST(INTRST_RATE_CHANGE_3MON_DV01 AS FLOAT) > 1000000;

28. "Show the total investment values grouped by currency code."
SELECT 
    CURRENCY_CODE,
    SUM(CAST(CURRENCY_VALUE AS FLOAT))
FROM 
    FUND_REPORTED_HOLDING 
GROUP BY 
    CURRENCY_CODE;

29. "List all borrowers with an aggregate value over 200 million."
SELECT 
    NAME,
    AGGREGATE_VALUE 
FROM 
    BORROWER 
WHERE 
    CAST(AGGREGATE_VALUE AS FLOAT) > 200000000;

30. "Which funds have unrealized appreciation in nonforeign currency swaps exceeding $10 million?"
SELECT 
    HOLDING_ID,
    UNREALIZED_APPRECIATION 
FROM 
    NONFOREIGN_EXCHANGE_SWAP 
WHERE 
    CAST(UNREALIZED_APPRECIATION AS FLOAT) > 10000000;

31. "List all funds with a liquidation preference exceeding $1 billion."
SELECT 
    SERIES_NAME,
    LIQUIDATION_PREFERENCE 
FROM 
    FUND_REPORTED_INFO 
WHERE 
    CAST(LIQUIDATION_PREFERENCE AS FLOAT) > 1000000000;

32. "Show me all debt securities with an annualized rate above 5%."
SELECT 
    HOLDING_ID,
    ANNUALIZED_RATE 
FROM 
    DEBT_SECURITY 
WHERE 
    CAST(ANNUALIZED_RATE AS FLOAT) > 5.0;

33. "Show all holding records with a balance over 1,000."
SELECT 
    ISSUER_NAME,
    BALANCE 
FROM 
    FUND_REPORTED_HOLDING 
WHERE 
    CAST(BALANCE AS FLOAT) > 1000;

34. "Show all funds with non-cash collateral flagged as true."
SELECT 
    SERIES_NAME,
    IS_NON_CASH_COLLATERAL 
FROM 
    FUND_REPORTED_INFO 
WHERE 
    IS_NON_CASH_COLLATERAL = 'Y';

35. "List all registrants reporting from countries other than the United States."
SELECT 
    REGISTRANT_NAME
FROM 
    REGISTRANT 
WHERE 
    COUNTRY != 'United States';

36. "Show all issuers categorized as DBT securities."
SELECT 
    ISSUER_NAME
FROM 
    FUND_REPORTED_HOLDING 
WHERE 
    ASSET_CAT = 'DBT';

37. "Find all funds where redemption flows in the second month are zero."
SELECT 
    SERIES_NAME
FROM 
    FUND_REPORTED_INFO 
WHERE 
    CAST(REDEMPTION_FLOW_MON2 AS FLOAT) = 0;

38. "Show all funds with cash not reported exceeding total liabilities."
SELECT 
    SERIES_NAME,
    CASH_NOT_RPTD_IN_C_OR_D,
    TOTAL_LIABILITIES 
FROM 
    FUND_REPORTED_INFO 
WHERE 
    CAST(CASH_NOT_RPTD_IN_C_OR_D AS FLOAT) > CAST(TOTAL_LIABILITIES AS FLOAT);

39. "Show all issuers with restricted securities."
SELECT 
    ISSUER_NAME
FROM 
    FUND_REPORTED_HOLDING 
WHERE 
    IS_RESTRICTED_SECURITY = 'Y';

40. "Find all funds where monthly sales flow for the second month is positive."
SELECT 
    SERIES_NAME,
    SALES_FLOW_MON2 
FROM 
    FUND_REPORTED_INFO 
WHERE 
    CAST(SALES_FLOW_MON2 AS FLOAT) > 0;
```
"""

gpt_queries_medium = """
```
Example queries set (medium difficulty) that should require join statements, but does not require any nested queries.

1. "How many funds does each registrant have?"
SELECT 
    REGISTRANT_NAME,
    COUNT(F.SERIES_NAME)
FROM 
    REGISTRANT R
    JOIN FUND_REPORTED_INFO F 
        ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
GROUP BY 
    REGISTRANT_NAME;

2. "What are the total assets of BlackRock funds?"
SELECT 
    SUM(CAST(TOTAL_ASSETS AS FLOAT))
FROM 
    FUND_REPORTED_INFO F
    JOIN REGISTRANT R 
        ON F.ACCESSION_NUMBER = R.ACCESSION_NUMBER
WHERE 
    R.REGISTRANT_NAME LIKE '%BLACKROCK%';

3. "List all funds with their registrant names"
SELECT 
    R.REGISTRANT_NAME,
    F.SERIES_NAME
FROM 
    REGISTRANT R
    JOIN FUND_REPORTED_INFO F 
        ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER;

4. "What's the latest filing date for each fund?"
SELECT 
    F.SERIES_NAME,
    MAX(S.FILING_DATE)
FROM 
    FUND_REPORTED_INFO F
    JOIN SUBMISSION S 
        ON F.ACCESSION_NUMBER = S.ACCESSION_NUMBER
GROUP BY 
    F.SERIES_NAME;

5. "Show me the earliest filing date for each registrant"
SELECT 
    R.REGISTRANT_NAME,
    MIN(S.FILING_DATE)
FROM 
    REGISTRANT R
    JOIN SUBMISSION S 
        ON R.ACCESSION_NUMBER = S.ACCESSION_NUMBER
GROUP BY 
    R.REGISTRANT_NAME;

6. "List all registrants with their fund count and total assets"
SELECT 
    R.REGISTRANT_NAME,
    COUNT(F.SERIES_NAME),
    SUM(CAST(F.TOTAL_ASSETS AS FLOAT))
FROM 
    REGISTRANT R
    JOIN FUND_REPORTED_INFO F 
        ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
GROUP BY 
    R.REGISTRANT_NAME;

7. "Show me all Fidelity funds"
SELECT 
    F.SERIES_NAME,
    F.TOTAL_ASSETS
FROM 
    FUND_REPORTED_INFO F
    JOIN REGISTRANT R 
        ON F.ACCESSION_NUMBER = R.ACCESSION_NUMBER
WHERE 
    R.REGISTRANT_NAME LIKE '%FIDELITY%';

8. "List all registrants with their latest fund's assets"
SELECT 
    R.REGISTRANT_NAME,
    F.TOTAL_ASSETS
FROM 
    REGISTRANT R
    JOIN FUND_REPORTED_INFO F 
        ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER;

9. "List all funds with their submission dates"
SELECT 
    F.SERIES_NAME,
    S.FILING_DATE
FROM 
    FUND_REPORTED_INFO F
    JOIN SUBMISSION S 
        ON F.ACCESSION_NUMBER = S.ACCESSION_NUMBER;

10. "Show me the registrants with the most recent filings"
SELECT 
    R.REGISTRANT_NAME,
    MAX(S.FILING_DATE)
FROM 
    REGISTRANT R
    JOIN SUBMISSION S 
        ON R.ACCESSION_NUMBER = S.ACCESSION_NUMBER
GROUP BY 
    R.REGISTRANT_NAME
ORDER BY 
    MAX(S.FILING_DATE) DESC
LIMIT 1;

11. "Find out which investment firms manage the most diverse portfolio of fund types?"
SELECT 
    R.REGISTRANT_NAME,
    COUNT(DISTINCT 
        CASE 
            WHEN F.SERIES_NAME LIKE '%BOND%' THEN 'BOND'
            WHEN F.SERIES_NAME LIKE '%EQUITY%' THEN 'EQUITY'
            WHEN F.SERIES_NAME LIKE '%MONEY MARKET%' THEN 'MONEY MARKET'
            WHEN F.SERIES_NAME LIKE '%INDEX%' THEN 'INDEX'
            WHEN F.SERIES_NAME LIKE '%ETF%' THEN 'ETF'
            ELSE 'OTHER'
        END
    ) AS Fund_Type_Count
FROM 
    REGISTRANT R
    JOIN FUND_REPORTED_INFO F 
        ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
GROUP BY 
    R.REGISTRANT_NAME
ORDER BY 
    Fund_Type_Count DESC
LIMIT 1;

12. "I need to check which funds may be too concentrated - find ones where a single holding is more than 10% of their portfolio?"
SELECT 
    F.SERIES_NAME,
    H.ISSUER_NAME,
    H.PERCENTAGE
FROM 
    FUND_REPORTED_INFO F
    JOIN FUND_REPORTED_HOLDING H 
        ON F.ACCESSION_NUMBER = H.ACCESSION_NUMBER
WHERE 
    CAST(H.PERCENTAGE AS FLOAT) > 10.0;

13. "Check which investment firms have the most diverse geographic exposure in their holdings"
SELECT 
    R.REGISTRANT_NAME,
    COUNT(DISTINCT H.INVESTMENT_COUNTRY),
    COUNT(DISTINCT H.HOLDING_ID)
FROM 
    REGISTRANT R
    JOIN FUND_REPORTED_INFO F 
        ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
    JOIN FUND_REPORTED_HOLDING H 
        ON F.ACCESSION_NUMBER = H.ACCESSION_NUMBER
WHERE 
    H.INVESTMENT_COUNTRY IS NOT NULL
GROUP BY 
    R.REGISTRANT_NAME
ORDER BY 
    COUNT(DISTINCT H.INVESTMENT_COUNTRY) DESC
LIMIT 1;

14. "Find me funds that might be too exposed to interest rate changes - check their duration risk"
SELECT 
    SERIES_NAME,
    CAST(INTRST_RATE_CHANGE_10YR_DV01 AS FLOAT),
    CAST(INTRST_RATE_CHANGE_30YR_DV01 AS FLOAT)
FROM 
    FUND_REPORTED_INFO F
    JOIN INTEREST_RATE_RISK IR 
        ON F.ACCESSION_NUMBER = IR.ACCESSION_NUMBER
WHERE 
    CAST(INTRST_RATE_CHANGE_10YR_DV01 AS FLOAT) > 1.0
    OR CAST(INTRST_RATE_CHANGE_30YR_DV01 AS FLOAT) > 1.0;

15. "I need to find funds with strong and consistent returns over all three months"
SELECT 
    F.SERIES_NAME,
    M.MONTHLY_TOTAL_RETURN1,
    M.MONTHLY_TOTAL_RETURN2,
    M.MONTHLY_TOTAL_RETURN3,
    (CAST(M.MONTHLY_TOTAL_RETURN1 AS FLOAT) + 
     CAST(M.MONTHLY_TOTAL_RETURN2 AS FLOAT) + 
     CAST(M.MONTHLY_TOTAL_RETURN3 AS FLOAT)) / 3
FROM 
    FUND_REPORTED_INFO F
    JOIN MONTHLY_TOTAL_RETURN M 
        ON F.ACCESSION_NUMBER = M.ACCESSION_NUMBER
WHERE 
    CAST(M.MONTHLY_TOTAL_RETURN1 AS FLOAT) > 0
    AND CAST(M.MONTHLY_TOTAL_RETURN2 AS FLOAT) > 0
    AND CAST(M.MONTHLY_TOTAL_RETURN3 AS FLOAT) > 0
ORDER BY 
    (CAST(M.MONTHLY_TOTAL_RETURN1 AS FLOAT) + 
     CAST(M.MONTHLY_TOTAL_RETURN2 AS FLOAT) + 
     CAST(M.MONTHLY_TOTAL_RETURN3 AS FLOAT)) / 3 DESC;

16. "Show me which asset categories had the best returns last month?"
SELECT 
    H.ASSET_CAT,
    AVG(CAST(M.MONTHLY_TOTAL_RETURN1 AS FLOAT))
FROM 
    FUND_REPORTED_HOLDING H
    JOIN FUND_REPORTED_INFO F 
        ON H.ACCESSION_NUMBER = F.ACCESSION_NUMBER
    JOIN MONTHLY_TOTAL_RETURN M 
        ON F.ACCESSION_NUMBER = M.ACCESSION_NUMBER
WHERE 
    H.ASSET_CAT IS NOT NULL
GROUP BY 
    H.ASSET_CAT
ORDER BY 
    AVG(CAST(M.MONTHLY_TOTAL_RETURN1 AS FLOAT)) DESC
LIMIT 1;

17. "Which investment companies are most exposed to international markets?"
SELECT 
    R.REGISTRANT_NAME,
    COUNT(CASE WHEN H.INVESTMENT_COUNTRY != 'US' THEN 1 END),
    COUNT(*),
    SUM(CASE WHEN H.INVESTMENT_COUNTRY != 'US' 
        THEN CAST(H.CURRENCY_VALUE AS FLOAT) ELSE 0 END)
FROM 
    REGISTRANT R
    JOIN FUND_REPORTED_INFO F 
        ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
    JOIN FUND_REPORTED_HOLDING H 
        ON F.ACCESSION_NUMBER = H.ACCESSION_NUMBER
GROUP BY 
    R.REGISTRANT_NAME
HAVING 
    COUNT(*) > 10
ORDER BY 
    COUNT(CASE WHEN H.INVESTMENT_COUNTRY != 'US' THEN 1 END) DESC
LIMIT 1;

18. "Help me find funds that might be too concentrated in specific sectors"
SELECT 
    F.SERIES_NAME,
    H.ASSET_CAT,
    CAST(SUM(H.CURRENCY_VALUE) AS FLOAT) / CAST(F.TOTAL_ASSETS AS FLOAT) * 100
FROM 
    FUND_REPORTED_INFO F
    JOIN FUND_REPORTED_HOLDING H 
        ON F.ACCESSION_NUMBER = H.ACCESSION_NUMBER
WHERE 
    H.ASSET_CAT IS NOT NULL
GROUP BY 
    F.SERIES_NAME, H.ASSET_CAT, F.TOTAL_ASSETS
ORDER BY 
    CAST(SUM(H.CURRENCY_VALUE) AS FLOAT) / CAST(F.TOTAL_ASSETS AS FLOAT) * 100 DESC;

19. "Which funds are taking on the most interest rate risk?"
SELECT 
    F.SERIES_NAME,
    CAST(IR.INTRST_RATE_CHANGE_10YR_DV01 AS FLOAT) + CAST(IR.INTRST_RATE_CHANGE_30YR_DV01 AS FLOAT)
FROM 
    FUND_REPORTED_INFO F
    JOIN INTEREST_RATE_RISK IR 
        ON F.ACCESSION_NUMBER = IR.ACCESSION_NUMBER
ORDER BY 
    CAST(IR.INTRST_RATE_CHANGE_10YR_DV01 AS FLOAT) + CAST(IR.INTRST_RATE_CHANGE_30YR_DV01 AS FLOAT) DESC
LIMIT 1;

20. "Identify funds with highest portfolio turnover based on their trading activity?"
SELECT 
    F.SERIES_NAME,
    (SUM(CAST(F.SALES_FLOW_MON1 AS FLOAT) + 
         CAST(F.SALES_FLOW_MON2 AS FLOAT) + 
         CAST(F.SALES_FLOW_MON3 AS FLOAT)) / NULLIF(CAST(F.TOTAL_ASSETS AS FLOAT), 0)) * 100
FROM 
    FUND_REPORTED_INFO F
WHERE 
    F.SALES_FLOW_MON1 IS NOT NULL 
    AND F.SALES_FLOW_MON2 IS NOT NULL 
    AND F.SALES_FLOW_MON3 IS NOT NULL
GROUP BY 
    F.SERIES_NAME, F.TOTAL_ASSETS
HAVING 
    F.TOTAL_ASSETS > 0
ORDER BY 
    (SUM(CAST(F.SALES_FLOW_MON1 AS FLOAT) + 
         CAST(F.SALES_FLOW_MON2 AS FLOAT) + 
         CAST(F.SALES_FLOW_MON3 AS FLOAT)) / NULLIF(CAST(F.TOTAL_ASSETS AS FLOAT), 0)) * 100 DESC
LIMIT 1;

21. "See which fund families are most active in securities lending"
SELECT 
    R.REGISTRANT_NAME
FROM 
    REGISTRANT R
    JOIN FUND_REPORTED_INFO F 
        ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
    LEFT JOIN SECURITIES_LENDING SL 
        ON F.ACCESSION_NUMBER = SL.HOLDING_ID
GROUP BY 
    R.REGISTRANT_NAME
ORDER BY 
    (COUNT(DISTINCT CASE WHEN SL.IS_LOAN_BY_FUND = 'Y' THEN F.SERIES_NAME END) * 100.0 / COUNT(DISTINCT F.SERIES_NAME)) DESC
LIMIT 1;

22. "How many funds does each investment company manage?"
SELECT 
    REGISTRANT_NAME,
    COUNT(DISTINCT SERIES_NAME),
    COUNT(DISTINCT SERIES_ID)
FROM 
    REGISTRANT R
    JOIN FUND_REPORTED_INFO F 
        ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
GROUP BY 
    REGISTRANT_NAME;

23. "Which USD funds are most exposed to interest rate changes?"
SELECT 
    F.SERIES_NAME
FROM 
    FUND_REPORTED_INFO F
    JOIN INTEREST_RATE_RISK IR 
        ON F.ACCESSION_NUMBER = IR.ACCESSION_NUMBER
WHERE 
    IR.CURRENCY_CODE = 'USD'
    AND (
        CAST(IR.INTRST_RATE_CHANGE_10YR_DV01 AS FLOAT) > 100000
        OR CAST(IR.INTRST_RATE_CHANGE_30YR_DV01 AS FLOAT) > 100000
    )
ORDER BY 
    CAST(IR.INTRST_RATE_CHANGE_10YR_DV01 AS FLOAT) DESC
LIMIT 1;

24. "What's our exposure by state? Need to check geographic concentration."
SELECT 
    R.STATE,
    SUM(CAST(F.TOTAL_ASSETS AS FLOAT))
FROM 
    REGISTRANT R
    JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
WHERE 
    R.STATE IS NOT NULL
GROUP BY 
    R.STATE;

25. "Which securities are most actively lent out?"
SELECT 
    H.ISSUER_NAME
FROM 
    FUND_REPORTED_HOLDING H
    JOIN SECURITIES_LENDING SL ON H.HOLDING_ID = SL.HOLDING_ID
WHERE 
    SL.IS_LOAN_BY_FUND = 'Y'
GROUP BY 
    H.ISSUER_NAME
HAVING 
    COUNT(*) > 1
ORDER BY 
    COUNT(*) DESC,
    SUM(CAST(H.CURRENCY_VALUE AS FLOAT)) DESC
LIMIT 1;

26. "Let's look at convertible securities with high conversion ratios - could be significant upside."
SELECT 
    F.SERIES_NAME,
    CSC.CONVERSION_RATIO
FROM 
    FUND_REPORTED_INFO F
    JOIN FUND_REPORTED_HOLDING H ON F.ACCESSION_NUMBER = H.ACCESSION_NUMBER
    JOIN CONVERTIBLE_SECURITY_CURRENCY CSC ON H.HOLDING_ID = CSC.HOLDING_ID
WHERE 
    CAST(CSC.CONVERSION_RATIO AS FLOAT) > 1
ORDER BY 
    CAST(CSC.CONVERSION_RATIO AS FLOAT) DESC;

27. "What percentage of bonds have missed interest payments by sector?"
SELECT
    h.ISSUER_TYPE,
    (COUNT(CASE WHEN d.ARE_ANY_INTEREST_PAYMENT = 'Y' THEN 1 END) * 100.0 / COUNT(*))
FROM 
    FUND_REPORTED_HOLDING h
    JOIN DEBT_SECURITY d ON h.HOLDING_ID = d.HOLDING_ID
WHERE 
    h.ISSUER_TYPE IS NOT NULL
GROUP BY 
    h.ISSUER_TYPE
ORDER BY 
    (COUNT(CASE WHEN d.ARE_ANY_INTEREST_PAYMENT = 'Y' THEN 1 END) * 100.0 / COUNT(*)) DESC;

28. “Find the total number of registrants and their average assets per state”
SELECT 
    R.STATE,
    COUNT(DISTINCT R.REGISTRANT_NAME),
    AVG(CAST(F.TOTAL_ASSETS AS FLOAT))
FROM 
    REGISTRANT R
LEFT JOIN 
    FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
WHERE 
    R.STATE IS NOT NULL
GROUP BY 
    R.STATE;

29. "List all funds and their associated registrants, sorted by filing date"
SELECT 
    R.REGISTRANT_NAME,
    F.SERIES_NAME,
    S.FILING_DATE
FROM 
    FUND_REPORTED_INFO F
    JOIN REGISTRANT R ON F.ACCESSION_NUMBER = R.ACCESSION_NUMBER
    JOIN SUBMISSION S ON F.ACCESSION_NUMBER = S.ACCESSION_NUMBER
ORDER BY 
    S.FILING_DATE DESC;

30. "What are the average total assets per state?"
SELECT 
    R.STATE,
    AVG(CAST(F.TOTAL_ASSETS AS FLOAT))
FROM 
    REGISTRANT R
    JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
WHERE 
    R.STATE IS NOT NULL
GROUP BY 
    R.STATE;

31. "List all funds managed by registrants in California."
SELECT 
    F.SERIES_NAME,
    R.REGISTRANT_NAME
FROM 
    FUND_REPORTED_INFO F
    JOIN REGISTRANT R ON F.ACCESSION_NUMBER = R.ACCESSION_NUMBER
WHERE 
    R.STATE = 'US-CA';

32. "Which registrants are most active in convertible securities?"
SELECT 
    R.REGISTRANT_NAME
FROM 
    REGISTRANT R
    JOIN FUND_REPORTED_HOLDING F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
    JOIN CONVERTIBLE_SECURITY_CURRENCY CSC ON F.HOLDING_ID = CSC.HOLDING_ID
GROUP BY 
    R.REGISTRANT_NAME
ORDER BY 
    COUNT(CSC.CONVERTIBLE_SECURITY_ID) DESC
LIMIT 1;

33. "Show funds exposed to non-cash collateral."
SELECT 
    R.REGISTRANT_NAME,
    F.SERIES_NAME
FROM 
    FUND_REPORTED_INFO F
    JOIN REGISTRANT R ON F.ACCESSION_NUMBER = R.ACCESSION_NUMBER
WHERE 
    F.IS_NON_CASH_COLLATERAL = 'Y';

34. "Which funds have the highest number of holdings?"
SELECT 
    F.SERIES_NAME
FROM 
    FUND_REPORTED_INFO F
    JOIN FUND_REPORTED_HOLDING H ON F.ACCESSION_NUMBER = H.ACCESSION_NUMBER
GROUP BY 
    F.SERIES_NAME
ORDER BY 
    COUNT(H.HOLDING_ID) DESC
LIMIT 1;

35. "List all funds managed by BlackRock and their total liabilities."
SELECT 
    F.SERIES_NAME,
    F.TOTAL_LIABILITIES
FROM 
    REGISTRANT R
    JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
WHERE 
    R.REGISTRANT_NAME LIKE '%BLACKROCK%';

36. "Identify funds managed by multiple registrants."
SELECT 
    F.SERIES_NAME,
    COUNT(DISTINCT R.REGISTRANT_NAME) AS REGISTRANT_COUNT
FROM 
    FUND_REPORTED_INFO F
    JOIN REGISTRANT R ON F.ACCESSION_NUMBER = R.ACCESSION_NUMBER
GROUP BY 
    F.SERIES_NAME
HAVING 
    COUNT(DISTINCT R.REGISTRANT_NAME) > 1;

37. "Which funds reported the highest borrowing within one year?"
SELECT 
    F.SERIES_NAME
FROM 
    FUND_REPORTED_INFO F
    JOIN REGISTRANT R ON F.ACCESSION_NUMBER = R.ACCESSION_NUMBER
GROUP BY 
    F.SERIES_NAME
ORDER BY
		MAX(CAST(F.BORROWING_PAY_WITHIN_1YR AS FLOAT)) DESC
LIMIT 1;

38. "Find registrants with securities in multiple countries."
SELECT 
    R.REGISTRANT_NAME
FROM 
    REGISTRANT R
    JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
    JOIN FUND_REPORTED_HOLDING H ON F.ACCESSION_NUMBER = H.ACCESSION_NUMBER
GROUP BY 
    R.REGISTRANT_NAME
HAVING 
    COUNT(DISTINCT H.INVESTMENT_COUNTRY) > 1;

39. "Which registrants have zero liabilities but manage funds?"
SELECT 
    R.REGISTRANT_NAME
FROM 
    REGISTRANT R
    JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
WHERE 
    F.TOTAL_LIABILITIES = '0'
GROUP BY 
    R.REGISTRANT_NAME;

40. "List all registrants along with the number of funds they manage."
SELECT 
    R.REGISTRANT_NAME,
    COUNT(F.SERIES_NAME)
FROM 
    REGISTRANT R
    JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
GROUP BY 
    R.REGISTRANT_NAME;
```
"""

gpt_queries_hard ="""
```
Example queries set (hard difficulty) that should require nested queries.

1. "Find funds whose total assets exceed the average total assets of all funds."
WITH AvgAssets AS (
    SELECT AVG(CAST(TOTAL_ASSETS AS FLOAT)) AS AVG_TOTAL_ASSETS
    FROM FUND_REPORTED_INFO
)
SELECT SERIES_NAME
FROM FUND_REPORTED_INFO
WHERE CAST(TOTAL_ASSETS AS FLOAT) > (SELECT AVG_TOTAL_ASSETS FROM AvgAssets);

2. "List the top 5 registrants by fund count, excluding those with below-average counts."
WITH AvgFundCount AS (
    SELECT AVG(FUND_COUNT) AS AVG_COUNT
    FROM (SELECT REGISTRANT_NAME, COUNT(*) AS FUND_COUNT FROM REGISTRANT R
          JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
          GROUP BY REGISTRANT_NAME) Subquery
)
SELECT REGISTRANT_NAME, COUNT(*)
FROM REGISTRANT R
JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
GROUP BY REGISTRANT_NAME
HAVING COUNT(*) > (SELECT AVG_COUNT FROM AvgFundCount)
ORDER BY COUNT(*) DESC
LIMIT 5;

3. "Show funds whose liabilities are more than twice the average liability of all funds."
WITH AvgLiabilities AS (
    SELECT AVG(CAST(TOTAL_LIABILITIES AS FLOAT)) AS AVG_LIABILITY
    FROM FUND_REPORTED_INFO
)
SELECT SERIES_NAME, TOTAL_LIABILITIES
FROM FUND_REPORTED_INFO
WHERE CAST(TOTAL_LIABILITIES AS FLOAT) > 2 * (SELECT AVG_LIABILITY FROM AvgLiabilities);

4. "Identify registrants whose states have the most funds."
WITH StateFundCount AS (
    SELECT STATE, COUNT(*) AS FUND_COUNT
    FROM REGISTRANT
    GROUP BY STATE
)
SELECT REGISTRANT_NAME, STATE
FROM REGISTRANT
WHERE STATE = (SELECT STATE FROM StateFundCount ORDER BY FUND_COUNT DESC LIMIT 1);

5. "Find funds whose total assets match the maximum total assets of their registrant's state."
WITH StateMaxAssets AS (
    SELECT STATE, MAX(CAST(TOTAL_ASSETS AS FLOAT)) AS MAX_ASSETS
    FROM REGISTRANT R
    JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
    GROUP BY STATE
)
SELECT SERIES_NAME, TOTAL_ASSETS, STATE
FROM REGISTRANT R
JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
WHERE CAST(TOTAL_ASSETS AS FLOAT) = (SELECT MAX_ASSETS FROM StateMaxAssets WHERE STATE = R.STATE);

6. "List the registrants whose funds account for more than 5% of total reported assets."
WITH TotalAssets AS (
    SELECT SUM(CAST(TOTAL_ASSETS AS FLOAT)) AS GLOBAL_TOTAL
    FROM FUND_REPORTED_INFO
)
SELECT REGISTRANT_NAME, SUM(CAST(F.TOTAL_ASSETS AS FLOAT))
FROM REGISTRANT R
JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
GROUP BY REGISTRANT_NAME
HAVING SUM(CAST(F.TOTAL_ASSETS AS FLOAT)) > 0.05 * (SELECT GLOBAL_TOTAL FROM TotalAssets);

7. "Find the largest fund for each registrant."
WITH LargestFunds AS (
    SELECT REGISTRANT_NAME, MAX(CAST(TOTAL_ASSETS AS FLOAT)) AS MAX_ASSETS
    FROM REGISTRANT R
    JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
    GROUP BY REGISTRANT_NAME
)
SELECT REGISTRANT_NAME, SERIES_NAME, TOTAL_ASSETS
FROM FUND_REPORTED_INFO F
JOIN REGISTRANT R ON F.ACCESSION_NUMBER = R.ACCESSION_NUMBER
WHERE CAST(TOTAL_ASSETS AS FLOAT) = (SELECT MAX_ASSETS FROM LargestFunds WHERE REGISTRANT_NAME = R.REGISTRANT_NAME);

8. "Show funds with liabilities exceeding 90% of the largest liability among all funds."
WITH MaxLiability AS (
    SELECT MAX(CAST(TOTAL_LIABILITIES AS FLOAT)) AS MAX_LIABILITY
    FROM FUND_REPORTED_INFO
)
SELECT SERIES_NAME, TOTAL_LIABILITIES
FROM FUND_REPORTED_INFO
WHERE CAST(TOTAL_LIABILITIES AS FLOAT) > 0.9 * (SELECT MAX_LIABILITY FROM MaxLiability);

9. "List funds whose net assets match their registrant's highest net asset fund."
WITH MaxNetAssets AS (
    SELECT REGISTRANT_NAME, MAX(CAST(NET_ASSETS AS FLOAT)) AS MAX_NET_ASSETS
    FROM REGISTRANT R
    JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
    GROUP BY REGISTRANT_NAME
)
SELECT SERIES_NAME, NET_ASSETS
FROM FUND_REPORTED_INFO F
JOIN REGISTRANT R ON F.ACCESSION_NUMBER = R.ACCESSION_NUMBER
WHERE CAST(NET_ASSETS AS FLOAT) = (SELECT MAX_NET_ASSETS FROM MaxNetAssets WHERE REGISTRANT_NAME = R.REGISTRANT_NAME);

10. "List registrants with above-average total assets in their state."
WITH StateAvgAssets AS (
    SELECT STATE, AVG(CAST(TOTAL_ASSETS AS FLOAT)) AS AVG_STATE_ASSETS
    FROM REGISTRANT R
    JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
    GROUP BY STATE
)
SELECT R.REGISTRANT_NAME, R.STATE, F.TOTAL_ASSETS
FROM REGISTRANT R
JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
WHERE CAST(F.TOTAL_ASSETS AS FLOAT) > (SELECT AVG_STATE_ASSETS FROM StateAvgAssets WHERE STATE = R.STATE);

11. "Identify funds whose liabilities exceed the largest liability for any bond fund."
WITH MaxBondLiability AS (
    SELECT MAX(CAST(TOTAL_LIABILITIES AS FLOAT)) AS MAX_BOND_LIABILITY
    FROM FUND_REPORTED_INFO
    WHERE SERIES_NAME LIKE '%BOND%'
)
SELECT SERIES_NAME, TOTAL_LIABILITIES
FROM FUND_REPORTED_INFO
WHERE CAST(TOTAL_LIABILITIES AS FLOAT) > (SELECT MAX_BOND_LIABILITY FROM MaxBondLiability);

12. "Show registrants managing the largest fund in each state."
WITH LargestFundPerState AS (
    SELECT R.STATE, MAX(CAST(F.TOTAL_ASSETS AS FLOAT)) AS MAX_ASSETS
    FROM REGISTRANT R
    JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
    GROUP BY R.STATE
)
SELECT R.REGISTRANT_NAME, R.STATE, F.SERIES_NAME, F.TOTAL_ASSETS
FROM REGISTRANT R
JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
WHERE CAST(F.TOTAL_ASSETS AS FLOAT) = (SELECT MAX_ASSETS FROM LargestFundPerState WHERE STATE = R.STATE);

13. "Find the smallest fund for each registrant."
WITH SmallestFunds AS (
    SELECT REGISTRANT_NAME, MIN(CAST(TOTAL_ASSETS AS FLOAT)) AS MIN_ASSETS
    FROM REGISTRANT R
    JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
    GROUP BY REGISTRANT_NAME
)
SELECT R.REGISTRANT_NAME, F.SERIES_NAME
FROM FUND_REPORTED_INFO F
JOIN REGISTRANT R ON F.ACCESSION_NUMBER = R.ACCESSION_NUMBER
WHERE CAST(F.TOTAL_ASSETS AS FLOAT) = (SELECT MIN_ASSETS FROM SmallestFunds WHERE REGISTRANT_NAME = R.REGISTRANT_NAME);

14. "List funds whose cash exceeds the average cash for their registrant."
WITH RegistrantAvgCash AS (
    SELECT REGISTRANT_NAME, AVG(CAST(CASH_NOT_RPTD_IN_C_OR_D AS FLOAT)) AS AVG_CASH
    FROM REGISTRANT R
    JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
    GROUP BY REGISTRANT_NAME
)
SELECT R.REGISTRANT_NAME, F.SERIES_NAME
FROM FUND_REPORTED_INFO F
JOIN REGISTRANT R ON F.ACCESSION_NUMBER = R.ACCESSION_NUMBER
WHERE CAST(F.CASH_NOT_RPTD_IN_C_OR_D AS FLOAT) > (SELECT AVG_CASH FROM RegistrantAvgCash WHERE REGISTRANT_NAME = R.REGISTRANT_NAME);

15. "Show states with above-average registrant counts."
WITH AvgRegistrantsPerState AS (
    SELECT AVG(REG_COUNT) AS AVG_COUNT
    FROM (SELECT STATE, COUNT(*) AS REG_COUNT FROM REGISTRANT GROUP BY STATE) Subquery
)
SELECT STATE
FROM REGISTRANT
GROUP BY STATE
HAVING COUNT(*) > (SELECT AVG_COUNT FROM AvgRegistrantsPerState);

16. "Find funds with net assets exceeding the maximum for equity funds."
WITH MaxEquityNetAssets AS (
    SELECT MAX(CAST(NET_ASSETS AS FLOAT)) AS MAX_NET_ASSETS
    FROM FUND_REPORTED_INFO
    WHERE SERIES_NAME LIKE '%EQUITY%'
)
SELECT SERIES_NAME, NET_ASSETS
FROM FUND_REPORTED_INFO
WHERE CAST(NET_ASSETS AS FLOAT) > (SELECT MAX_NET_ASSETS FROM MaxEquityNetAssets);

17. "List registrants managing the largest fund across all registrants."
WITH LargestFund AS (
    SELECT MAX(CAST(TOTAL_ASSETS AS FLOAT)) AS MAX_TOTAL_ASSETS
    FROM FUND_REPORTED_INFO
)
SELECT R.REGISTRANT_NAME, F.SERIES_NAME, F.TOTAL_ASSETS
FROM REGISTRANT R
JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
WHERE CAST(F.TOTAL_ASSETS AS FLOAT) = (SELECT MAX_TOTAL_ASSETS FROM LargestFund);

18. "Identify funds with liabilities less than the smallest liability for bond funds."
WITH MinBondLiability AS (
    SELECT MIN(CAST(TOTAL_LIABILITIES AS FLOAT)) AS MIN_BOND_LIABILITY
    FROM FUND_REPORTED_INFO
    WHERE SERIES_NAME LIKE '%BOND%'
)
SELECT SERIES_NAME, TOTAL_LIABILITIES
FROM FUND_REPORTED_INFO
WHERE CAST(TOTAL_LIABILITIES AS FLOAT) < (SELECT MIN_BOND_LIABILITY FROM MinBondLiability);

19. "Find the largest fund in each state."
WITH StateLargestFund AS (
    SELECT STATE, MAX(CAST(TOTAL_ASSETS AS FLOAT)) AS MAX_ASSETS
    FROM REGISTRANT R
    JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
    GROUP BY STATE
)
SELECT R.STATE, F.SERIES_NAME, F.TOTAL_ASSETS
FROM REGISTRANT R
JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
WHERE CAST(F.TOTAL_ASSETS AS FLOAT) = (SELECT MAX_ASSETS FROM StateLargestFund WHERE STATE = R.STATE);

20. "Show funds with a percentage of their portfolio in cash exceeding 20%."
WITH CashPercentage AS (
    SELECT SERIES_NAME, (CAST(CASH_NOT_RPTD_IN_C_OR_D AS FLOAT) / CAST(TOTAL_ASSETS AS FLOAT)) AS CASH_RATIO
    FROM FUND_REPORTED_INFO
    WHERE CASH_NOT_RPTD_IN_C_OR_D IS NOT NULL AND CAST(TOTAL_ASSETS AS FLOAT) > 0
)
SELECT SERIES_NAME, CASH_RATIO
FROM CashPercentage
WHERE CASH_RATIO > 0.2;

21. "Identify funds with above-average monthly redemption flows."
WITH AvgRedemptionFlow AS (
    SELECT AVG(CAST(REDEMPTION_FLOW_MON1 AS FLOAT) + CAST(REDEMPTION_FLOW_MON2 AS FLOAT) + CAST(REDEMPTION_FLOW_MON3 AS FLOAT)) AS AVG_FLOW
    FROM FUND_REPORTED_INFO
)
SELECT SERIES_NAME, REDEMPTION_FLOW_MON1, REDEMPTION_FLOW_MON2, REDEMPTION_FLOW_MON3
FROM FUND_REPORTED_INFO
WHERE (CAST(REDEMPTION_FLOW_MON1 AS FLOAT) + CAST(REDEMPTION_FLOW_MON2 AS FLOAT) + CAST(REDEMPTION_FLOW_MON3 AS FLOAT)) > (SELECT AVG_FLOW FROM AvgRedemptionFlow);

22. "Find registrants whose largest fund exceeds $1 billion in total assets."
WITH LargestFundPerRegistrant AS (
    SELECT REGISTRANT_NAME, MAX(CAST(TOTAL_ASSETS AS FLOAT)) AS MAX_ASSETS
    FROM REGISTRANT R
    JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
    GROUP BY REGISTRANT_NAME
)
SELECT REGISTRANT_NAME, MAX_ASSETS
FROM LargestFundPerRegistrant
WHERE MAX_ASSETS > 1000000000;

23. "Show funds with liabilities smaller than the smallest liability of any bond fund."
WITH MinBondFundLiability AS (
    SELECT MIN(CAST(TOTAL_LIABILITIES AS FLOAT)) AS MIN_LIABILITY
    FROM FUND_REPORTED_INFO
    WHERE SERIES_NAME LIKE '%BOND%'
)
SELECT SERIES_NAME, TOTAL_LIABILITIES
FROM FUND_REPORTED_INFO
WHERE CAST(TOTAL_LIABILITIES AS FLOAT) < (SELECT MIN_LIABILITY FROM MinBondFundLiability);

24. "Find the total cash held by registrants whose largest fund exceeds $500 million."
WITH RegistrantsWithLargeFunds AS (
    SELECT REGISTRANT_NAME
    FROM REGISTRANT R
    JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
    GROUP BY REGISTRANT_NAME
    HAVING MAX(CAST(F.TOTAL_ASSETS AS FLOAT)) > 500000000
)
SELECT R.REGISTRANT_NAME, SUM(CAST(F.CASH_NOT_RPTD_IN_C_OR_D AS FLOAT)) AS TOTAL_CASH
FROM REGISTRANT R
JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
WHERE R.REGISTRANT_NAME IN (SELECT REGISTRANT_NAME FROM RegistrantsWithLargeFunds)
GROUP BY R.REGISTRANT_NAME;

25. "List funds that have a greater percentage of cash compared to any equity fund."
WITH MaxEquityCashRatio AS (
    SELECT MAX(CAST(CASH_NOT_RPTD_IN_C_OR_D AS FLOAT) / CAST(TOTAL_ASSETS AS FLOAT)) AS MAX_EQUITY_CASH_RATIO
    FROM FUND_REPORTED_INFO
    WHERE SERIES_NAME LIKE '%EQUITY%'
)
SELECT SERIES_NAME, CASH_NOT_RPTD_IN_C_OR_D, TOTAL_ASSETS
FROM FUND_REPORTED_INFO
WHERE CAST(CASH_NOT_RPTD_IN_C_OR_D AS FLOAT) / CAST(TOTAL_ASSETS AS FLOAT) > (SELECT MAX_EQUITY_CASH_RATIO FROM MaxEquityCashRatio);

26. "Identify states with more than 10 registrants having net assets above the average."
WITH AvgNetAssets AS (
    SELECT AVG(CAST(NET_ASSETS AS FLOAT)) AS AVG_NET_ASSETS
    FROM FUND_REPORTED_INFO
)
SELECT R.STATE, COUNT(*) AS REGISTRANT_COUNT
FROM REGISTRANT R
JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
WHERE CAST(F.NET_ASSETS AS FLOAT) > (SELECT AVG_NET_ASSETS FROM AvgNetAssets)
GROUP BY R.STATE
HAVING COUNT(*) > 10;

27. "Show registrants with the largest portfolio turnover ratio."
WITH PortfolioTurnover AS (
    SELECT REGISTRANT_NAME, 
           MAX((CAST(F.SALES_FLOW_MON1 AS FLOAT) + CAST(F.SALES_FLOW_MON2 AS FLOAT) + CAST(F.SALES_FLOW_MON3 AS FLOAT)) 
               / CAST(F.TOTAL_ASSETS AS FLOAT)) AS TURNOVER_RATIO
    FROM REGISTRANT R
    JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
    GROUP BY REGISTRANT_NAME
)
SELECT REGISTRANT_NAME, TURNOVER_RATIO
FROM PortfolioTurnover
ORDER BY TURNOVER_RATIO DESC
LIMIT 1;

28. "Find funds whose liabilities are larger than the average liabilities of bond funds."
WITH AvgBondLiability AS (
    SELECT AVG(CAST(TOTAL_LIABILITIES AS FLOAT)) AS AVG_BOND_LIABILITY
    FROM FUND_REPORTED_INFO
    WHERE SERIES_NAME LIKE '%BOND%'
)
SELECT SERIES_NAME, TOTAL_LIABILITIES
FROM FUND_REPORTED_INFO
WHERE CAST(TOTAL_LIABILITIES AS FLOAT) > (SELECT AVG_BOND_LIABILITY FROM AvgBondLiability);

29. "Identify states where the largest fund is managed by Vanguard."
WITH VanguardLargestFund AS (
    SELECT STATE, MAX(CAST(TOTAL_ASSETS AS FLOAT)) AS MAX_ASSETS
    FROM REGISTRANT R
    JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
    WHERE R.REGISTRANT_NAME LIKE '%VANGUARD%'
    GROUP BY STATE
)
SELECT STATE, MAX_ASSETS
FROM VanguardLargestFund;

30. "Find exisiting funds with the highest proportion of liabilities to net assets."
WITH LiabilityToNetAssets AS (
    SELECT SERIES_NAME, 
           (CAST(TOTAL_LIABILITIES AS FLOAT) / CAST(NET_ASSETS AS FLOAT)) AS LIABILITY_RATIO
    FROM FUND_REPORTED_INFO
    WHERE CAST(NET_ASSETS AS FLOAT) > 0
)
SELECT SERIES_NAME, LIABILITY_RATIO
FROM LiabilityToNetAssets
WHERE SERIES_NAME != 'N/A'
ORDER BY LIABILITY_RATIO DESC
LIMIT 1;

31. "Identify funds with monthly sales flows larger than any ETF."
WITH MaxETFSalesFlow AS (
    SELECT MAX(CAST(SALES_FLOW_MON1 AS FLOAT) + CAST(SALES_FLOW_MON2 AS FLOAT) + CAST(SALES_FLOW_MON3 AS FLOAT)) AS MAX_ETF_FLOW
    FROM FUND_REPORTED_INFO
    WHERE SERIES_NAME LIKE '%ETF%'
)
SELECT SERIES_NAME, SALES_FLOW_MON1, SALES_FLOW_MON2, SALES_FLOW_MON3
FROM FUND_REPORTED_INFO
WHERE (CAST(SALES_FLOW_MON1 AS FLOAT) + CAST(SALES_FLOW_MON2 AS FLOAT) + CAST(SALES_FLOW_MON3 AS FLOAT)) > (SELECT MAX_ETF_FLOW FROM MaxETFSalesFlow);

32. "Identify funds whose cash proportion is higher than the average cash proportion of equity funds."
WITH AvgEquityCashRatio AS (
    SELECT AVG(CAST(CASH_NOT_RPTD_IN_C_OR_D AS FLOAT) / CAST(TOTAL_ASSETS AS FLOAT)) AS AVG_CASH_RATIO
    FROM FUND_REPORTED_INFO
    WHERE SERIES_NAME LIKE '%EQUITY%' AND CAST(TOTAL_ASSETS AS FLOAT) > 0
)
SELECT SERIES_NAME, CASH_NOT_RPTD_IN_C_OR_D, TOTAL_ASSETS
FROM FUND_REPORTED_INFO
WHERE (CAST(CASH_NOT_RPTD_IN_C_OR_D AS FLOAT) / CAST(TOTAL_ASSETS AS FLOAT)) > (SELECT AVG_CASH_RATIO FROM AvgEquityCashRatio);

33. "Show registrants managing funds with liabilities higher than any convertible security fund."
WITH MaxConvertibleLiability AS (
    SELECT MAX(CAST(TOTAL_LIABILITIES AS FLOAT)) AS MAX_CONVERTIBLE_LIABILITY
    FROM FUND_REPORTED_INFO
    WHERE SERIES_NAME LIKE '%CONVERTIBLE%'
)
SELECT R.REGISTRANT_NAME, F.SERIES_NAME, F.TOTAL_LIABILITIES
FROM REGISTRANT R
JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
WHERE CAST(F.TOTAL_LIABILITIES AS FLOAT) > (SELECT MAX_CONVERTIBLE_LIABILITY FROM MaxConvertibleLiability);

34. "List funds with monthly sales flows higher than the average for all funds."
WITH AvgSalesFlow AS (
    SELECT AVG(CAST(SALES_FLOW_MON1 AS FLOAT) + CAST(SALES_FLOW_MON2 AS FLOAT) + CAST(SALES_FLOW_MON3 AS FLOAT)) AS AVG_SALES_FLOW
    FROM FUND_REPORTED_INFO
)
SELECT SERIES_NAME, SALES_FLOW_MON1, SALES_FLOW_MON2, SALES_FLOW_MON3
FROM FUND_REPORTED_INFO
WHERE (CAST(SALES_FLOW_MON1 AS FLOAT) + CAST(SALES_FLOW_MON2 AS FLOAT) + CAST(SALES_FLOW_MON3 AS FLOAT)) > (SELECT AVG_SALES_FLOW FROM AvgSalesFlow);

35. "Find funds with liabilities less than the average liabilities of all funds in their state."
WITH AvgStateLiability AS (
    SELECT R.STATE, AVG(CAST(F.TOTAL_LIABILITIES AS FLOAT)) AS AVG_LIABILITY
    FROM REGISTRANT R
    JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
    GROUP BY R.STATE
)
SELECT F.SERIES_NAME, F.TOTAL_LIABILITIES, R.STATE
FROM FUND_REPORTED_INFO F
JOIN REGISTRANT R ON F.ACCESSION_NUMBER = R.ACCESSION_NUMBER
WHERE CAST(F.TOTAL_LIABILITIES AS FLOAT) < (SELECT AVG_LIABILITY FROM AvgStateLiability WHERE STATE = R.STATE);

36. "Identify registrants managing funds with the highest cash proportion in their state."
WITH StateMaxCash AS (
    SELECT R.STATE, MAX(CAST(F.CASH_NOT_RPTD_IN_C_OR_D AS FLOAT) / CAST(F.TOTAL_ASSETS AS FLOAT)) AS MAX_CASH_RATIO
    FROM REGISTRANT R
    JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
    WHERE CAST(F.TOTAL_ASSETS AS FLOAT) > 0
    GROUP BY R.STATE
)
SELECT R.REGISTRANT_NAME, R.STATE, F.SERIES_NAME, F.CASH_NOT_RPTD_IN_C_OR_D
FROM REGISTRANT R
JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
WHERE CAST(F.CASH_NOT_RPTD_IN_C_OR_D AS FLOAT) / CAST(F.TOTAL_ASSETS AS FLOAT) = 
      (SELECT MAX_CASH_RATIO FROM StateMaxCash WHERE STATE = R.STATE);

37. "Find states with total liabilities higher than the average liabilities for all states."
WITH AvgStateLiability AS (
    SELECT R.STATE, AVG(CAST(F.TOTAL_LIABILITIES AS FLOAT)) AS AVG_STATE_LIABILITY
    FROM REGISTRANT R
    JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
    GROUP BY R.STATE
)
SELECT STATE
FROM AvgStateLiability
WHERE AVG_STATE_LIABILITY > (SELECT AVG(AVG_STATE_LIABILITY) FROM AvgStateLiability);

38. "Show registrants managing funds with liabilities larger than the maximum liabilities of any index fund."
WITH MaxIndexFundLiability AS (
    SELECT MAX(CAST(TOTAL_LIABILITIES AS FLOAT)) AS MAX_INDEX_LIABILITY
    FROM FUND_REPORTED_INFO
    WHERE SERIES_NAME LIKE '%INDEX%'
)
SELECT R.REGISTRANT_NAME, F.SERIES_NAME, F.TOTAL_LIABILITIES
FROM REGISTRANT R
JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
WHERE CAST(F.TOTAL_LIABILITIES AS FLOAT) > (SELECT MAX_INDEX_LIABILITY FROM MaxIndexFundLiability);

39. "Find funds whose redemption flows exceed the highest redemption flow for any bond fund."
WITH MaxBondRedemptionFlow AS (
    SELECT MAX(CAST(REDEMPTION_FLOW_MON1 AS FLOAT) + CAST(REDEMPTION_FLOW_MON2 AS FLOAT) + CAST(REDEMPTION_FLOW_MON3 AS FLOAT)) AS MAX_BOND_FLOW
    FROM FUND_REPORTED_INFO
    WHERE SERIES_NAME LIKE '%BOND%'
)
SELECT SERIES_NAME, REDEMPTION_FLOW_MON1, REDEMPTION_FLOW_MON2, REDEMPTION_FLOW_MON3
FROM FUND_REPORTED_INFO
WHERE (CAST(REDEMPTION_FLOW_MON1 AS FLOAT) + CAST(REDEMPTION_FLOW_MON2 AS FLOAT) + CAST(REDEMPTION_FLOW_MON3 AS FLOAT)) > (SELECT MAX_BOND_FLOW FROM MaxBondRedemptionFlow);

40. "List states with the highest average net assets per fund."
WITH StateAvgNetAssets AS (
    SELECT R.STATE, AVG(CAST(F.NET_ASSETS AS FLOAT)) AS AVG_NET_ASSETS
    FROM REGISTRANT R
    JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
    WHERE F.NET_ASSETS IS NOT NULL
    GROUP BY R.STATE
)
SELECT STATE, AVG_NET_ASSETS
FROM StateAvgNetAssets
WHERE AVG_NET_ASSETS = (SELECT MAX(AVG_NET_ASSETS) FROM StateAvgNetAssets);
```
"""

# Full prompt 
full_prompt = (
    overall_task_instructions +
    database_overview_instructions +
    schema_info +
    nlp_query_handling_instructions +
    default_query_behavior +
    reasoning_instruction +
    example_queries +
    gpt_queries_easy +
    #gpt_queries_medium +
    #gpt_queries_hard +
    output_instruction
)

common_part_prompt = (
    overall_task_instructions +
    database_overview_instructions +
    schema_info +
    nlp_query_handling_instructions +
    default_query_behavior +
    reasoning_instruction +
    schema_info +
    example_queries
)

import openai
import logging
from fastapi import HTTPException

# Set up the logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Construct the function that takes in the user's question 
# and returning the SQL commands with reasoning in json format
def generate_sql_and_reasoning(user_question: str) -> dict:
    # Append the user question to the full prompt
    prompt_with_question = full_prompt + f"\n\nUser Question: {user_question}\n"

    try:
        # Call the OpenAI API to generate the SQL query and reasoning
        response = openai.Completion.create(
            engine="gpt-3.5-turbo",  # Adjust model if needed
            prompt=prompt_with_question,
            max_tokens=300,  # Adjust token limit as per your need
            temperature=0.7
        )

        # Extract the reasoning and the SQL query from the response
        generated_text = response.choices[0].text.strip()

        # Assuming reasoning and SQL are separated by a newline in the response
        reasoning, sql_query = generated_text.split("\n", 1)

        return {
            "reasoning": reasoning.strip(),
            "SQL Query": sql_query.strip()
        }

    except openai.error.OpenAIError as e:
        logger.error(f"Error with OpenAI API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error generating SQL: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    

schema_linking_prompt = '''Table advisor, columns = [*,s_ID,i_ID]
Table classroom, columns = [*,building,room_number,capacity]
Table course, columns = [*,course_id,title,dept_name,credits]
Table department, columns = [*,dept_name,building,budget]
Table instructor, columns = [*,ID,name,dept_name,salary]
Table prereq, columns = [*,course_id,prereq_id]
Table section, columns = [*,course_id,sec_id,semester,year,building,room_number,time_slot_id]
Table student, columns = [*,ID,name,dept_name,tot_cred]
Table takes, columns = [*,ID,course_id,sec_id,semester,year,grade]
Table teaches, columns = [*,ID,course_id,sec_id,semester,year]
Table time_slot, columns = [*,time_slot_id,day,start_hr,start_min,end_hr,end_min]
Foreign_keys = [course.dept_name = department.dept_name,instructor.dept_name = department.dept_name,section.building = classroom.building,section.room_number = classroom.room_number,section.course_id = course.course_id,teaches.ID = instructor.ID,teaches.course_id = section.course_id,teaches.sec_id = section.sec_id,teaches.semester = section.semester,teaches.year = section.year,student.dept_name = department.dept_name,takes.ID = student.ID,takes.course_id = section.course_id,takes.sec_id = section.sec_id,takes.semester = section.semester,takes.year = section.year,advisor.s_ID = student.ID,advisor.i_ID = instructor.ID,prereq.prereq_id = course.course_id,prereq.course_id = course.course_id]
Q: "Find the buildings which have rooms with capacity more than 50."
A: Let’s think step by step. In the question "Find the buildings which have rooms with capacity more than 50.", we are asked:
"the buildings which have rooms" so we need column = [classroom.capacity]
"rooms with capacity" so we need column = [classroom.building]
Based on the columns and tables, we need these Foreign_keys = [].
Based on the tables, columns, and Foreign_keys, The set of possible cell values are = [50]. So the Schema_links are:
Schema_links: [classroom.building,classroom.capacity,50]

Table department, columns = [*,Department_ID,Name,Creation,Ranking,Budget_in_Billions,Num_Employees]
Table head, columns = [*,head_ID,name,born_state,age]
Table management, columns = [*,department_ID,head_ID,temporary_acting]
Foreign_keys = [management.head_ID = head.head_ID,management.department_ID = department.Department_ID]
Q: "How many heads of the departments are older than 56 ?"
A: Let’s think step by step. In the question "How many heads of the departments are older than 56 ?", we are asked:
"How many heads of the departments" so we need column = [head.*]
"older" so we need column = [head.age]
Based on the columns and tables, we need these Foreign_keys = [].
Based on the tables, columns, and Foreign_keys, The set of possible cell values are = [56]. So the Schema_links are:
Schema_links: [head.*,head.age,56]

Table department, columns = [*,Department_ID,Name,Creation,Ranking,Budget_in_Billions,Num_Employees]
Table head, columns = [*,head_ID,name,born_state,age]
Table management, columns = [*,department_ID,head_ID,temporary_acting]
Foreign_keys = [management.head_ID = head.head_ID,management.department_ID = department.Department_ID]
Q: "what are the distinct creation years of the departments managed by a secretary born in state 'Alabama'?"
A: Let’s think step by step. In the question "what are the distinct creation years of the departments managed by a secretary born in state 'Alabama'?", we are asked:
"distinct creation years of the departments" so we need column = [department.Creation]
"departments managed by" so we need column = [management.department_ID]
"born in" so we need column = [head.born_state]
Based on the columns and tables, we need these Foreign_keys = [department.Department_ID = management.department_ID,management.head_ID = head.head_ID].
Based on the tables, columns, and Foreign_keys, The set of possible cell values are = ['Alabama']. So the Schema_links are:
Schema_links: [department.Creation,department.Department_ID = management.department_ID,head.head_ID = management.head_ID,head.born_state,'Alabama']

Table Addresses, columns = [*,address_id,line_1,line_2,city,zip_postcode,state_province_county,country]
Table Candidate_Assessments, columns = [*,candidate_id,qualification,assessment_date,asessment_outcome_code]
Table Candidates, columns = [*,candidate_id,candidate_details]
Table Courses, columns = [*,course_id,course_name,course_description,other_details]
Table People, columns = [*,person_id,first_name,middle_name,last_name,cell_mobile_number,email_address,login_name,password]
Table People_Addresses, columns = [*,person_address_id,person_id,address_id,date_from,date_to]
Table Student_Course_Attendance, columns = [*,student_id,course_id,date_of_attendance]
Table Student_Course_Registrations, columns = [*,student_id,course_id,registration_date]
Table Students, columns = [*,student_id,student_details]
Foreign_keys = [Students.student_id = People.person_id,People_Addresses.address_id = Addresses.address_id,People_Addresses.person_id = People.person_id,Student_Course_Registrations.course_id = Courses.course_id,Student_Course_Registrations.student_id = Students.student_id,Student_Course_Attendance.student_id = Student_Course_Registrations.student_id,Student_Course_Attendance.course_id = Student_Course_Registrations.course_id,Candidates.candidate_id = People.person_id,Candidate_Assessments.candidate_id = Candidates.candidate_id]
Q: "List the id of students who never attends courses?"
A: Let’s think step by step. In the question "List the id of students who never attends courses?", we are asked:
"id of students" so we need column = [Students.student_id]
"never attends courses" so we need column = [Student_Course_Attendance.student_id]
Based on the columns and tables, we need these Foreign_keys = [Students.student_id = Student_Course_Attendance.student_id].
Based on the tables, columns, and Foreign_keys, The set of possible cell values are = []. So the Schema_links are:
Schema_links: [Students.student_id = Student_Course_Attendance.student_id]

Table Country, columns = [*,id,name]
Table League, columns = [*,id,country_id,name]
Table Player, columns = [*,id,player_api_id,player_name,player_fifa_api_id,birthday,height,weight]
Table Player_Attributes, columns = [*,id,player_fifa_api_id,player_api_id,date,overall_rating,potential,preferred_foot,attacking_work_rate,defensive_work_rate,crossing,finishing,heading_accuracy,short_passing,volleys,dribbling,curve,free_kick_accuracy,long_passing,ball_control,acceleration,sprint_speed,agility,reactions,balance,shot_power,jumping,stamina,strength,long_shots,aggression,interceptions,positioning,vision,penalties,marking,standing_tackle,sliding_tackle,gk_diving,gk_handling,gk_kicking,gk_positioning,gk_reflexes]
Table Team, columns = [*,id,team_api_id,team_fifa_api_id,team_long_name,team_short_name]
Table Team_Attributes, columns = [*,id,team_fifa_api_id,team_api_id,date,buildUpPlaySpeed,buildUpPlaySpeedClass,buildUpPlayDribbling,buildUpPlayDribblingClass,buildUpPlayPassing,buildUpPlayPassingClass,buildUpPlayPositioningClass,chanceCreationPassing,chanceCreationPassingClass,chanceCreationCrossing,chanceCreationCrossingClass,chanceCreationShooting,chanceCreationShootingClass,chanceCreationPositioningClass,defencePressure,defencePressureClass,defenceAggression,defenceAggressionClass,defenceTeamWidth,defenceTeamWidthClass,defenceDefenderLineClass]
Table sqlite_sequence, columns = [*,name,seq]
Foreign_keys = [Player_Attributes.player_api_id = Player.player_api_id,Player_Attributes.player_fifa_api_id = Player.player_fifa_api_id,League.country_id = Country.id,Team_Attributes.team_api_id = Team.team_api_id,Team_Attributes.team_fifa_api_id = Team.team_fifa_api_id]
Q: "List the names of all left-footed players who have overall rating between 85 and 90."
A: Let’s think step by step. In the question "List the names of all left-footed players who have overall rating between 85 and 90.", we are asked:
"names of all left-footed players" so we need column = [Player.player_name,Player_Attributes.preferred_foot]
"players who have overall rating" so we need column = [Player_Attributes.overall_rating]
Based on the columns and tables, we need these Foreign_keys = [Player_Attributes.player_api_id = Player.player_api_id].
Based on the tables, columns, and Foreign_keys, The set of possible cell values are = [left,85,90]. So the Schema_links are:
Schema_links: [Player.player_name,Player_Attributes.preferred_foot,Player_Attributes.overall_rating,Player_Attributes.player_api_id = Player.player_api_id,left,85,90]

Table advisor, columns = [*,s_ID,i_ID]
Table classroom, columns = [*,building,room_number,capacity]
Table course, columns = [*,course_id,title,dept_name,credits]
Table department, columns = [*,dept_name,building,budget]
Table instructor, columns = [*,ID,name,dept_name,salary]
Table prereq, columns = [*,course_id,prereq_id]
Table section, columns = [*,course_id,sec_id,semester,year,building,room_number,time_slot_id]
Table student, columns = [*,ID,name,dept_name,tot_cred]
Table takes, columns = [*,ID,course_id,sec_id,semester,year,grade]
Table teaches, columns = [*,ID,course_id,sec_id,semester,year]
Table time_slot, columns = [*,time_slot_id,day,start_hr,start_min,end_hr,end_min]
Foreign_keys = [course.dept_name = department.dept_name,instructor.dept_name = department.dept_name,section.building = classroom.building,section.room_number = classroom.room_number,section.course_id = course.course_id,teaches.ID = instructor.ID,teaches.course_id = section.course_id,teaches.sec_id = section.sec_id,teaches.semester = section.semester,teaches.year = section.year,student.dept_name = department.dept_name,takes.ID = student.ID,takes.course_id = section.course_id,takes.sec_id = section.sec_id,takes.semester = section.semester,takes.year = section.year,advisor.s_ID = student.ID,advisor.i_ID = instructor.ID,prereq.prereq_id = course.course_id,prereq.course_id = course.course_id]
Q: "Give the title of the course offered in Chandler during the Fall of 2010."
A: Let’s think step by step. In the question "Give the title of the course offered in Chandler during the Fall of 2010.", we are asked:
"title of the course" so we need column = [course.title]
"course offered in Chandler" so we need column = [SECTION.building]
"during the Fall" so we need column = [SECTION.semester]
"of 2010" so we need column = [SECTION.year]
Based on the columns and tables, we need these Foreign_keys = [course.course_id = SECTION.course_id].
Based on the tables, columns, and Foreign_keys, The set of possible cell values are = [Chandler,Fall,2010]. So the Schema_links are:
Schema_links: [course.title,course.course_id = SECTION.course_id,SECTION.building,SECTION.year,SECTION.semester,Chandler,Fall,2010]

Table city, columns = [*,City_ID,Official_Name,Status,Area_km_2,Population,Census_Ranking]
Table competition_record, columns = [*,Competition_ID,Farm_ID,Rank]
Table farm, columns = [*,Farm_ID,Year,Total_Horses,Working_Horses,Total_Cattle,Oxen,Bulls,Cows,Pigs,Sheep_and_Goats]
Table farm_competition, columns = [*,Competition_ID,Year,Theme,Host_city_ID,Hosts]
Foreign_keys = [farm_competition.Host_city_ID = city.City_ID,competition_record.Farm_ID = farm.Farm_ID,competition_record.Competition_ID = farm_competition.Competition_ID]
Q: "Show the status of the city that has hosted the greatest number of competitions."
A: Let’s think step by step. In the question "Show the status of the city that has hosted the greatest number of competitions.", we are asked:
"the status of the city" so we need column = [city.Status]
"greatest number of competitions" so we need column = [farm_competition.*]
Based on the columns and tables, we need these Foreign_keys = [farm_competition.Host_city_ID = city.City_ID].
Based on the tables, columns, and Foreign_keys, The set of possible cell values are = []. So the Schema_links are:
Schema_links: [city.Status,farm_competition.Host_city_ID = city.City_ID,farm_competition.*]

Table advisor, columns = [*,s_ID,i_ID]
Table classroom, columns = [*,building,room_number,capacity]
Table course, columns = [*,course_id,title,dept_name,credits]
Table department, columns = [*,dept_name,building,budget]
Table instructor, columns = [*,ID,name,dept_name,salary]
Table prereq, columns = [*,course_id,prereq_id]
Table section, columns = [*,course_id,sec_id,semester,year,building,room_number,time_slot_id]
Table student, columns = [*,ID,name,dept_name,tot_cred]
Table takes, columns = [*,ID,course_id,sec_id,semester,year,grade]
Table teaches, columns = [*,ID,course_id,sec_id,semester,year]
Table time_slot, columns = [*,time_slot_id,day,start_hr,start_min,end_hr,end_min]
Foreign_keys = [course.dept_name = department.dept_name,instructor.dept_name = department.dept_name,section.building = classroom.building,section.room_number = classroom.room_number,section.course_id = course.course_id,teaches.ID = instructor.ID,teaches.course_id = section.course_id,teaches.sec_id = section.sec_id,teaches.semester = section.semester,teaches.year = section.year,student.dept_name = department.dept_name,takes.ID = student.ID,takes.course_id = section.course_id,takes.sec_id = section.sec_id,takes.semester = section.semester,takes.year = section.year,advisor.s_ID = student.ID,advisor.i_ID = instructor.ID,prereq.prereq_id = course.course_id,prereq.course_id = course.course_id]
Q: "Find the id of instructors who taught a class in Fall 2009 but not in Spring 2010."
A: Let’s think step by step. In the question "Find the id of instructors who taught a class in Fall 2009 but not in Spring 2010.", we are asked:
"id of instructors who taught " so we need column = [teaches.id]
"taught a class in" so we need column = [teaches.semester,teaches.year]
Based on the columns and tables, we need these Foreign_keys = [].
Based on the tables, columns, and Foreign_keys, The set of possible cell values are = [Fall,2009,Spring,2010]. So the Schema_links are:
schema_links: [teaches.id,teaches.semester,teaches.year,Fall,2009,Spring,2010]

Table Accounts, columns = [*,account_id,customer_id,date_account_opened,account_name,other_account_details]
Table Customers, columns = [*,customer_id,customer_first_name,customer_middle_initial,customer_last_name,gender,email_address,login_name,login_password,phone_number,town_city,state_county_province,country]
Table Financial_Transactions, columns = [*,transaction_id,account_id,invoice_number,transaction_type,transaction_date,transaction_amount,transaction_comment,other_transaction_details]
Table Invoice_Line_Items, columns = [*,order_item_id,invoice_number,product_id,product_title,product_quantity,product_price,derived_product_cost,derived_vat_payable,derived_total_cost]
Table Invoices, columns = [*,invoice_number,order_id,invoice_date]
Table Order_Items, columns = [*,order_item_id,order_id,product_id,product_quantity,other_order_item_details]
Table Orders, columns = [*,order_id,customer_id,date_order_placed,order_details]
Table Product_Categories, columns = [*,production_type_code,product_type_description,vat_rating]
Table Products, columns = [*,product_id,parent_product_id,production_type_code,unit_price,product_name,product_color,product_size]
Foreign_keys = [Orders.customer_id = Customers.customer_id,Invoices.order_id = Orders.order_id,Accounts.customer_id = Customers.customer_id,Products.production_type_code = Product_Categories.production_type_code,Financial_Transactions.account_id = Accounts.account_id,Financial_Transactions.invoice_number = Invoices.invoice_number,Order_Items.order_id = Orders.order_id,Order_Items.product_id = Products.product_id,Invoice_Line_Items.product_id = Products.product_id,Invoice_Line_Items.invoice_number = Invoices.invoice_number,Invoice_Line_Items.order_item_id = Order_Items.order_item_id]
Q: "Show the id, the date of account opened, the account name, and other account detail for all accounts."
A: Let’s think step by step. In the question "Show the id, the date of account opened, the account name, and other account detail for all accounts.", we are asked:
"the id, the date of account opened, the account name, and other account detail for all accounts." so we need column = [Accounts.account_id,Accounts.account_name,Accounts.other_account_details,Accounts.date_account_opened]
Based on the columns and tables, we need these Foreign_keys = [].
Based on the tables, columns, and Foreign_keys, The set of possible cell values are = []. So the Schema_links are:
Schema_links: [Accounts.account_id,Accounts.account_name,Accounts.other_account_details,Accounts.date_account_opened]

Table city, columns = [*,City_ID,Official_Name,Status,Area_km_2,Population,Census_Ranking]
Table competition_record, columns = [*,Competition_ID,Farm_ID,Rank]
Table farm, columns = [*,Farm_ID,Year,Total_Horses,Working_Horses,Total_Cattle,Oxen,Bulls,Cows,Pigs,Sheep_and_Goats]
Table farm_competition, columns = [*,Competition_ID,Year,Theme,Host_city_ID,Hosts]
Foreign_keys = [farm_competition.Host_city_ID = city.City_ID,competition_record.Farm_ID = farm.Farm_ID,competition_record.Competition_ID = farm_competition.Competition_ID]
Q: "Show the status shared by cities with population bigger than 1500 and smaller than 500."
A: Let’s think step by step. In the question "Show the status shared by cities with population bigger than 1500 and smaller than 500.", we are asked:
"the status shared by cities" so we need column = [city.Status]
"cities with population" so we need column = [city.Population]
Based on the columns and tables, we need these Foreign_keys = [].
Based on the tables, columns, and Foreign_keys, The set of possible cell values are = [1500,500]. So the Schema_links are:
Schema_links: [city.Status,city.Population,1500,500]

'''