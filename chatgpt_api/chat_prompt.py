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
- The Database combines information from 30 tables of the NPORT dataset from quarter 4 of 2019 to quarter 3 of 2024.
- The data includes a comprehensive view of fund-level information, holdings, debt securities, repurchase agreements, and derivative instruments.
- Each relation represents detailed information about financial transactions, security holdings, and fund performance, including key identifiers like ACCESSION_NUMBER, HOLDING_ID, and CUSIP for borrowers, holdings, and securities.
- The table provides essential metrics like total assets, liabilities, interest rate risks, monthly returns, and details for securities lending and collateral.
- The table aggregates all the data to provide a holistic view of financial activities for the 2019q4 to 2024q3 period.
```
"""

# Schema information as plain text with descriptions for each column in the database
schema_info = """
Schema description:
Below is the schema desciprtion of some tables and their attributes

```
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
```
```
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
```
```
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
```
```
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
```
```
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
```
```
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
```
```
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
```
```
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
```
```
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
```
```
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
```
```
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
```
```
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
```
```
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
```
```
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
```
```
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
```
```
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
```
```
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
```
```
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
```
```
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
```
```
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
```
```
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
```
```
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
```
```
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
```
```
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
```
```
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
```
```
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
```
```
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
```
```
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
```
```
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
```
```
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
- Default to the most recent time period ('2024q3') if not specified, and consider all asset classes unless otherwise mentioned.
```
"""

# Define default behavior for unspecified fields or conditions
default_query_behavior = f"""
```
Default values and assumptions:
- Assume the most recent filing period ('{latest_time_period}') if no time period is specified, which is indicated by QUARTER column in the database.
- Include all asset classes and sectors unless specified in the query.
- Retrieve all filings if no specific criteria are provided.
```
"""

# Example Natural Language Queries and Corresponding SQL Translations
example_queries = """
```
Example queries set 1, where Natural language request is encased in double quotations " and desired output is the SQL query after 'SQL:'
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

2. "Find all holdings with a fair value level of Level 1 and their corresponding fund names."
   SQL: 
   WITH HoldingsCTE AS (
       SELECT H.HOLDING_ID, H.ISSUER_NAME, H.FAIR_VALUE_LEVEL, F.SERIES_NAME
       FROM FUND_REPORTED_HOLDING H
       JOIN FUND_REPORTED_INFO F ON H.ACCESSION_NUMBER = F.ACCESSION_NUMBER
       WHERE H.FAIR_VALUE_LEVEL = 'Level 1'
   )
   SELECT HOLDING_ID, ISSUER_NAME, SERIES_NAME
   FROM HoldingsCTE;

3. "Calculate the total collateral amount for repurchase agreements grouped by counterparty."
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

4. "Locate funds that have both securities lending activities and repurchase agreements."
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

5. "Find borrowers who have borrowed more than $5,000,000, including their names and LEIs."
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

6. "List all derivative counterparties along with the number of derivative instruments they are involved in."
   SQL: 
   WITH CounterpartyCounts AS (
       SELECT DC.DERIVATIVE_COUNTERPARTY_NAME, COUNT(*) AS Instrument_Count
       FROM DERIVATIVE_COUNTERPARTY DC
       JOIN FUND_REPORTED_HOLDING H ON DC.HOLDING_ID = H.HOLDING_ID
       JOIN DEBT_SECURITY D ON H.HOLDING_ID = D.HOLDING_ID
       GROUP BY DC.DERIVATIVE_COUNTERPARTY_NAME
   )
   SELECT DERIVATIVE_COUNTERPARTY_NAME, Instrument_Count
   FROM CounterpartyCounts
   ORDER BY Instrument_Count DESC;

7. "Compute the average annualized rate for debt securities grouped by coupon type."
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

8. "Get funds that have experienced a net decrease in assets over the last three reporting periods."
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

9. "Identify issuers with more than three different securities holdings, including their names and CUSIPs."
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

10. "Calculate the total notional amount of derivatives per currency and identify the top 3 currencies by notional amount."
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

11. "List funds with liquidation preferences exceeding their net assets."
    SQL: 
    WITH FundPreferences AS (
        SELECT F.SERIES_NAME, F.LIQUIDATION_PREFERENCE, F.NET_ASSETS
        FROM FUND_REPORTED_INFO F
    )
    SELECT SERIES_NAME, LIQUIDATION_PREFERENCE, NET_ASSETS
    FROM FundPreferences
    WHERE LIQUIDATION_PREFERENCE > NET_ASSETS;

12. "Find all convertible securities that are contingent and have a conversion ratio above 1.5."
    SQL: 
    WITH ConvertibleCTE AS (
        SELECT DS.HOLDING_ID, CSC.CONVERSION_RATIO
        FROM DEBT_SECURITY DS
        JOIN CONVERTIBLE_SECURITY_CURRENCY CSC ON DS.HOLDING_ID = CSC.HOLDING_ID
        WHERE DS.IS_CONVTIBLE_CONTINGENT = 'Y' AND CSC.CONVERSION_RATIO > 1.5
    )
    SELECT HOLDING_ID, CONVERSION_RATIO
    FROM ConvertibleCTE;

13. "Retrieve the total unrealized appreciation for each asset category across all funds."
    SQL: 
    WITH AppreciationCTE AS (
        SELECT H.ASSET_CAT, SUM(H.PERCENTAGE * H.CURRENCY_VALUE) AS Total_Unrealized_App
        FROM FUND_REPORTED_HOLDING H
        GROUP BY H.ASSET_CAT
    )
    SELECT ASSET_CAT, Total_Unrealized_App
    FROM AppreciationCTE
    ORDER BY Total_Unrealized_App DESC;

14. "Analyze the distribution of asset categories within the top 10 largest funds by total assets."
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

```
"""


example_queries_2 = """
```
Example queries set 2, where Natural language request is encased in double quotations " and desired output is the SQL query after 'SQL:'
1. "Find the top 10 funds with the highest average monthly returns in the past quarter."
   SQL: 
   WITH AvgMonthlyReturn AS (
       SELECT ACCESSION_NUMBER, 
              (MONTHLY_TOTAL_RETURN1 + MONTHLY_TOTAL_RETURN2 + MONTHLY_TOTAL_RETURN3) / 3.0 AS Avg_Return
       FROM MONTHLY_TOTAL_RETURN
   )
   SELECT F.SERIES_NAME, A.ACCESSION_NUMBER, A.Avg_Return
   FROM AvgMonthlyReturn A
   JOIN FUND_REPORTED_INFO F ON A.ACCESSION_NUMBER = F.ACCESSION_NUMBER
   ORDER BY A.Avg_Return DESC
   LIMIT 10;

2. "Compare the latest net asset values of the top 5 performing funds."
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

3. "Calculate the overall average return across all funds for the most recent month."
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

4. "Find the interest rate risk for each fund and identify those with the highest risk scores."
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

5. "Determine which funds have the highest Value at Risk (VaR) based on their variable information."
   SQL: 
   WITH FundVaR AS (
       SELECT ACCESSION_NUMBER, 
              (VAR1 + VAR2 + VAR3) AS Total_VaR
       FROM FUND_VAR_INFO
   )
   SELECT F.SERIES_NAME, FV.ACCESSION_NUMBER, FV.Total_VaR
   FROM FundVaR FV
   JOIN FUND_REPORTED_INFO F ON FV.ACCESSION_NUMBER = F.ACCESSION_NUMBER
   ORDER BY FV.Total_VaR DESC
   LIMIT 5;

6. "Retrieve funds that have experienced a net decrease in assets over the last three reporting periods."
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

7. "Analyze the composition of fund portfolios by categorizing assets and their total values."
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

8. "Identify the most common asset categories across all fund portfolios."
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

9. "Determine the percentage allocation of each asset category within individual fund portfolios."
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

10. "Identify funds with significant derivative exposures exceeding one million in unrealized appreciation."
    SQL: 
    WITH SignificantExposures AS (
        SELECT F.ACCESSION_NUMBER, F.SERIES_NAME, SUM(D.UNREALIZED_APPRECIATION) AS Total_Derivative_Exposure
        FROM SWAPTION_OPTION_WARNT_DERIV D
        JOIN FUND_REPORTED_HOLDING FH ON D.HOLDING_ID = FH.HOLDING_ID
        JOIN FUND_REPORTED_INFO F ON FH.ACCESSION_NUMBER = F.ACCESSION_NUMBER
        GROUP BY F.ACCESSION_NUMBER, F.SERIES_NAME
        HAVING SUM(D.UNREALIZED_APPRECIATION) > 1000000
    )
    SELECT SERIES_NAME, ACCESSION_NUMBER, Total_Derivative_Exposure
    FROM SignificantExposures
    ORDER BY Total_Derivative_Exposure DESC;

```
"""

# Reasoning instructions
reasoning_instruction = """

```
Reasoning Instructions:
1. Reasoning you provide should first focus on why a nested query was chosen or why it wasn't chosen.
2. It should give a query plan on how to solve this question - explain 
the mapping of the columns to the words in the input question.
3. It should explain each of the clauses and why they are structured the way they are structured. 
   For example, if there is a `GROUP BY`, an explanation should be given as to why it exists.
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

# Full prompt 
full_prompt = (
    overall_task_instructions +
    #table_name_instructions +
    database_overview_instructions +
    nlp_query_handling_instructions +
    #sql_query_template_instructions +
    default_query_behavior +
    example_queries +
    example_queries_2 +
    reasoning_instruction +
    output_instruction
)
# Output the full prompt
print(full_prompt)


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