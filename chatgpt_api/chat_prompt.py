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

13. "Find the top 10 funds with the highest average monthly returns in the past quarter."
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

gpt_queries_easy = """
```
1. "Show me the top 5 largest funds by total assets"
SELECT 
    SERIES_NAME,
    TOTAL_ASSETS 
FROM 
    FUND_REPORTED_INFO 
ORDER BY 
    CAST(TOTAL_ASSETS AS FLOAT) DESC 
LIMIT 5;

2. "Which registrants are based in New York?"
SELECT 
    REGISTRANT_NAME,
    ADDRESS1,
    PHONE 
FROM 
    REGISTRANT 
WHERE 
    STATE = 'NY';

3. "List all funds with net assets over 1 billion dollars"
SELECT 
    SERIES_NAME,
    NET_ASSETS 
FROM 
    FUND_REPORTED_INFO 
WHERE 
    CAST(NET_ASSETS AS FLOAT) > 1000000000;

4. "How many funds does each registrant have?"
SELECT 
    REGISTRANT_NAME,
    COUNT(F.SERIES_NAME) as Fund_Count
FROM 
    REGISTRANT R
    JOIN FUND_REPORTED_INFO F 
        ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
GROUP BY 
    REGISTRANT_NAME;

5. "What are the total assets of BlackRock funds?"
SELECT 
    SUM(CAST(TOTAL_ASSETS AS FLOAT)) as Total_BlackRock_Assets
FROM 
    FUND_REPORTED_INFO F
    JOIN REGISTRANT R 
        ON F.ACCESSION_NUMBER = R.ACCESSION_NUMBER
WHERE 
    R.REGISTRANT_NAME LIKE '%BLACKROCK%';

6. "List all funds with their registrant names"
SELECT 
    R.REGISTRANT_NAME,
    F.SERIES_NAME
FROM 
    REGISTRANT R
    JOIN FUND_REPORTED_INFO F 
        ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER;

7. "Which funds have the highest total liabilities?"
SELECT 
    SERIES_NAME,
    TOTAL_LIABILITIES 
FROM 
    FUND_REPORTED_INFO 
ORDER BY 
    CAST(TOTAL_LIABILITIES AS FLOAT) DESC 
LIMIT 10;

8. "Show me all registrants in California"
SELECT 
    REGISTRANT_NAME,
    CITY,
    PHONE 
FROM 
    REGISTRANT 
WHERE 
    STATE = 'CA';

9. "What's the latest filing date for each fund?"
SELECT 
    F.SERIES_NAME,
    MAX(S.FILING_DATE) as Latest_Filing
FROM 
    FUND_REPORTED_INFO F
    JOIN SUBMISSION S 
        ON F.ACCESSION_NUMBER = S.ACCESSION_NUMBER
GROUP BY 
    F.SERIES_NAME;

10. "List all funds with negative net assets"
SELECT 
    SERIES_NAME,
    NET_ASSETS 
FROM 
    FUND_REPORTED_INFO 
WHERE 
    CAST(NET_ASSETS AS FLOAT) < 0;

11. "Show me the phone numbers of all Vanguard registrants"
SELECT 
    REGISTRANT_NAME,
    PHONE 
FROM 
    REGISTRANT 
WHERE 
    REGISTRANT_NAME LIKE '%VANGUARD%';

12. "Which funds have assets between 100M and 500M?"
SELECT 
    SERIES_NAME,
    TOTAL_ASSETS 
FROM 
    FUND_REPORTED_INFO 
WHERE 
    CAST(TOTAL_ASSETS AS FLOAT) BETWEEN 100000000 AND 500000000;

13. "List all registrants and their cities"
SELECT 
    REGISTRANT_NAME,
    CITY,
    STATE 
FROM 
    REGISTRANT 
ORDER BY 
    STATE,
    CITY;

14. "Show me the earliest filing date for each registrant"
SELECT 
    R.REGISTRANT_NAME,
    MIN(S.FILING_DATE) as First_Filing
FROM 
    REGISTRANT R
    JOIN SUBMISSION S 
        ON R.ACCESSION_NUMBER = S.ACCESSION_NUMBER
GROUP BY 
    R.REGISTRANT_NAME;

15. "Which funds have total assets equal to net assets?"
SELECT 
    SERIES_NAME 
FROM 
    FUND_REPORTED_INFO 
WHERE 
    TOTAL_ASSETS = NET_ASSETS;

16. "List all funds with 'Income' in their name"
SELECT 
    SERIES_NAME,
    TOTAL_ASSETS 
FROM 
    FUND_REPORTED_INFO 
WHERE 
    SERIES_NAME LIKE '%INCOME%';

17. "Show me all registrants in Texas with their CIK numbers"
SELECT 
    REGISTRANT_NAME,
    CIK,
    CITY 
FROM 
    REGISTRANT 
WHERE 
    STATE = 'TX';

18. "Which funds have the highest liabilities to assets ratio?"
SELECT 
    SERIES_NAME,
    CAST(TOTAL_LIABILITIES AS FLOAT) / CAST(TOTAL_ASSETS AS FLOAT) as Liability_Ratio
FROM 
    FUND_REPORTED_INFO
WHERE 
    TOTAL_ASSETS != '0'
ORDER BY 
    Liability_Ratio DESC
LIMIT 5;

19. "List all registrants with their fund count and total assets"
SELECT 
    R.REGISTRANT_NAME,
    COUNT(F.SERIES_NAME) as Fund_Count,
    SUM(CAST(F.TOTAL_ASSETS AS FLOAT)) as Total_Assets
FROM 
    REGISTRANT R
    JOIN FUND_REPORTED_INFO F 
        ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
GROUP BY 
    R.REGISTRANT_NAME;

20. "Show me all funds with 'Growth' in their name"
SELECT 
    SERIES_NAME,
    TOTAL_ASSETS 
FROM 
    FUND_REPORTED_INFO 
WHERE 
    SERIES_NAME LIKE '%GROWTH%';

21. "Which registrants are from Illinois?"
SELECT 
    REGISTRANT_NAME,
    CITY,
    ADDRESS1 
FROM 
    REGISTRANT 
WHERE 
    STATE = 'IL';

22. "List the top 10 funds by net assets"
SELECT 
    SERIES_NAME,
    NET_ASSETS 
FROM 
    FUND_REPORTED_INFO 
ORDER BY 
    CAST(NET_ASSETS AS FLOAT) DESC 
LIMIT 10;

23. "Show me all Fidelity funds"
SELECT 
    F.SERIES_NAME,
    F.TOTAL_ASSETS
FROM 
    FUND_REPORTED_INFO F
    JOIN REGISTRANT R 
        ON F.ACCESSION_NUMBER = R.ACCESSION_NUMBER
WHERE 
    R.REGISTRANT_NAME LIKE '%FIDELITY%';

24. "Which funds have zero liabilities?"
SELECT 
    SERIES_NAME 
FROM 
    FUND_REPORTED_INFO 
WHERE 
    TOTAL_LIABILITIES = '0' 
    OR TOTAL_LIABILITIES IS NULL;

25. "List all registrants with their latest fund's assets"
SELECT 
    R.REGISTRANT_NAME,
    F.TOTAL_ASSETS
FROM 
    REGISTRANT R
    JOIN FUND_REPORTED_INFO F 
        ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER;

26. "Show me all funds with 'International' in their name"
SELECT 
    SERIES_NAME,
    TOTAL_ASSETS 
FROM 
    FUND_REPORTED_INFO 
WHERE 
    SERIES_NAME LIKE '%INTERNATIONAL%';

27. "Which registrants are from Massachusetts?"
SELECT 
    REGISTRANT_NAME,
    CITY,
    PHONE 
FROM 
    REGISTRANT 
WHERE 
    STATE = 'MA';

28. "List all funds with their submission dates"
SELECT 
    F.SERIES_NAME,
    S.FILING_DATE
FROM 
    FUND_REPORTED_INFO F
    JOIN SUBMISSION S 
        ON F.ACCESSION_NUMBER = S.ACCESSION_NUMBER;

29. "Show me the smallest 5 funds by total assets"
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

30. "Which registrants have multiple phone numbers?"
SELECT 
    REGISTRANT_NAME,
    COUNT(DISTINCT PHONE) as Phone_Count
FROM 
    REGISTRANT
GROUP BY 
    REGISTRANT_NAME
HAVING 
    Phone_Count > 1;

31. "List all funds with 'Bond' in their name"
SELECT 
    SERIES_NAME,
    TOTAL_ASSETS 
FROM 
    FUND_REPORTED_INFO 
WHERE 
    SERIES_NAME LIKE '%BOND%';

32. "Show me all registrants from Florida"
SELECT 
    REGISTRANT_NAME,
    CITY,
    ADDRESS1 
FROM 
    REGISTRANT 
WHERE 
    STATE = 'FL';

33. "Which funds were filed in 2023?"
SELECT 
    F.SERIES_NAME,
    S.FILING_DATE
FROM 
    FUND_REPORTED_INFO F
    JOIN SUBMISSION S 
        ON F.ACCESSION_NUMBER = S.ACCESSION_NUMBER
WHERE 
    S.FILING_DATE LIKE '2023%';

34. "List all funds with 'Index' in their name"
SELECT 
    SERIES_NAME,
    TOTAL_ASSETS 
FROM 
    FUND_REPORTED_INFO 
WHERE 
    SERIES_NAME LIKE '%INDEX%';

35. "Show me the registrants with the most recent filings"
SELECT 
    R.REGISTRANT_NAME,
    MAX(S.FILING_DATE) as Latest_Filing
FROM 
    REGISTRANT R
    JOIN SUBMISSION S 
        ON R.ACCESSION_NUMBER = S.ACCESSION_NUMBER
GROUP BY 
    R.REGISTRANT_NAME
ORDER BY 
    Latest_Filing DESC
LIMIT 5;

36. "Which funds have 'ETF' in their name?"
SELECT 
    SERIES_NAME,
    TOTAL_ASSETS 
FROM 
    FUND_REPORTED_INFO 
WHERE 
    SERIES_NAME LIKE '%ETF%';

37. "List all registrants with their ZIP codes"
SELECT 
    REGISTRANT_NAME,
    ZIP,
    STATE 
FROM 
    REGISTRANT 
ORDER BY 
    ZIP;

38. "Show me all funds from T. Rowe Price"
SELECT 
    F.SERIES_NAME,
    F.TOTAL_ASSETS
FROM 
    FUND_REPORTED_INFO F
    JOIN REGISTRANT R 
        ON F.ACCESSION_NUMBER = R.ACCESSION_NUMBER
WHERE 
    R.REGISTRANT_NAME LIKE '%T ROWE%';

39. "Which funds have assets over 10 billion?"
SELECT 
    SERIES_NAME,
    TOTAL_ASSETS 
FROM 
    FUND_REPORTED_INFO 
WHERE 
    CAST(TOTAL_ASSETS AS FLOAT) > 10000000000;

40. "List all registrants with their country"
SELECT 
    REGISTRANT_NAME,
    COUNTRY,
    STATE 
FROM 
    REGISTRANT 
ORDER BY 
    COUNTRY,
    STATE;
```
"""

gpt_queries_medium = """
```
1. "Can you show me which funds have had the biggest increase in total assets over the last quarter?"
WITH AssetChanges AS (
    SELECT 
        F1.SERIES_NAME,
        F1.TOTAL_ASSETS as Current_Assets,
        F2.TOTAL_ASSETS as Previous_Assets
    FROM 
        FUND_REPORTED_INFO F1
        JOIN SUBMISSION S1 
            ON F1.ACCESSION_NUMBER = S1.ACCESSION_NUMBER
        JOIN FUND_REPORTED_INFO F2 
            ON F1.SERIES_NAME = F2.SERIES_NAME
        JOIN SUBMISSION S2 
            ON F2.ACCESSION_NUMBER = S2.ACCESSION_NUMBER
    WHERE 
        S1.QUARTER = '2023Q4'
        AND S2.QUARTER = '2023Q3'
)
SELECT 
    SERIES_NAME,
    CAST(Current_Assets AS FLOAT) - CAST(Previous_Assets AS FLOAT) as Asset_Growth
FROM 
    AssetChanges
ORDER BY 
    Asset_Growth DESC
LIMIT 10;

2. "I'm looking for any funds with 'sustainable' or 'ESG' in their name - what's their total AUM?"
WITH ESGFunds AS (
    SELECT 
        SERIES_NAME,
        TOTAL_ASSETS
    FROM 
        FUND_REPORTED_INFO
    WHERE 
        SERIES_NAME LIKE '%SUSTAINABLE%'
        OR SERIES_NAME LIKE '%ESG%'
)
SELECT 
    COUNT(*) as Number_of_ESG_Funds,
    SUM(CAST(TOTAL_ASSETS AS FLOAT)) as Total_ESG_Assets
FROM 
    ESGFunds;

3. "Could you check which states have the most fund registrants? Top 5 would be great."
WITH StateRegistrants AS (
    SELECT 
        STATE,
        COUNT(DISTINCT REGISTRANT_NAME) as Registrant_Count,
        COUNT(DISTINCT F.SERIES_NAME) as Fund_Count
    FROM 
        REGISTRANT R
        LEFT JOIN FUND_REPORTED_INFO F 
            ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
    WHERE 
        STATE IS NOT NULL
    GROUP BY 
        STATE
)
SELECT 
    STATE,
    Registrant_Count,
    Fund_Count
FROM 
    StateRegistrants
ORDER BY 
    Registrant_Count DESC
LIMIT 5;

4. "I need to find any funds that have more liabilities than assets - bit concerning if there are any!"
WITH FundHealth AS (
    SELECT 
        SERIES_NAME,
        CAST(TOTAL_ASSETS AS FLOAT) as Assets,
        CAST(TOTAL_LIABILITIES AS FLOAT) as Liabilities,
        CAST(TOTAL_LIABILITIES AS FLOAT) / NULLIF(CAST(TOTAL_ASSETS AS FLOAT), 0) as Liability_Ratio
    FROM 
        FUND_REPORTED_INFO
    WHERE 
        TOTAL_ASSETS IS NOT NULL 
        AND TOTAL_LIABILITIES IS NOT NULL
)
SELECT 
    SERIES_NAME,
    Assets,
    Liabilities,
    Liability_Ratio
FROM 
    FundHealth
WHERE 
    Liabilities > Assets
ORDER BY 
    Liability_Ratio DESC;

5. Find out which investment firms manage the most diverse portfolio of fund types?"
WITH FundTypes AS (
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
        ) as Fund_Type_Count
    FROM 
        REGISTRANT R
        JOIN FUND_REPORTED_INFO F 
            ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
    GROUP BY 
        R.REGISTRANT_NAME
)
SELECT 
    REGISTRANT_NAME,
    Fund_Type_Count
FROM 
    FundTypes
WHERE 
    Fund_Type_Count > 2
ORDER BY 
    Fund_Type_Count DESC
LIMIT 10;

6. "I need to check which funds might be too concentrated - find ones where a single holding is more than 10% of their portfolio?"
WITH HoldingConcentration AS (
    SELECT 
        F.SERIES_NAME,
        H.ISSUER_NAME,
        H.PERCENTAGE,
        F.TOTAL_ASSETS
    FROM 
        FUND_REPORTED_INFO F
        JOIN FUND_REPORTED_HOLDING H 
            ON F.ACCESSION_NUMBER = H.ACCESSION_NUMBER
    WHERE 
        CAST(H.PERCENTAGE AS FLOAT) > 10.0
)
SELECT 
    SERIES_NAME,
    ISSUER_NAME,
    PERCENTAGE,
    TOTAL_ASSETS
FROM 
    HoldingConcentration
ORDER BY 
    CAST(PERCENTAGE AS FLOAT) DESC;

7. "Compare how our bond funds performed against equity funds in the last month"
WITH FundReturns AS (
    SELECT 
        F.SERIES_NAME,
        CASE 
            WHEN F.SERIES_NAME LIKE '%BOND%' THEN 'Bond'
            WHEN F.SERIES_NAME LIKE '%EQUITY%' THEN 'Equity'
        END as Fund_Type,
        M.MONTHLY_TOTAL_RETURN1
    FROM 
        FUND_REPORTED_INFO F
        JOIN MONTHLY_TOTAL_RETURN M 
            ON F.ACCESSION_NUMBER = M.ACCESSION_NUMBER
    WHERE 
        F.SERIES_NAME LIKE '%BOND%'
        OR F.SERIES_NAME LIKE '%EQUITY%'
)
SELECT 
    Fund_Type,
    AVG(CAST(MONTHLY_TOTAL_RETURN1 AS FLOAT)) as Avg_Return,
    COUNT(*) as Fund_Count
FROM 
    FundReturns
GROUP BY 
    Fund_Type;

8. "Which investment firms seem to be growing the fastest based on their asset growth?"
WITH AssetGrowth AS (
    SELECT 
        R.REGISTRANT_NAME,
        SUM(CAST(F.TOTAL_ASSETS AS FLOAT)) as Current_Assets,
        LAG(SUM(CAST(F.TOTAL_ASSETS AS FLOAT))) OVER (
            PARTITION BY R.REGISTRANT_NAME 
            ORDER BY S.FILING_DATE
        ) as Previous_Assets,
        S.FILING_DATE
    FROM 
        REGISTRANT R
        JOIN FUND_REPORTED_INFO F 
            ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
        JOIN SUBMISSION S 
            ON F.ACCESSION_NUMBER = S.ACCESSION_NUMBER
    GROUP BY 
        R.REGISTRANT_NAME,
        S.FILING_DATE
)
SELECT 
    REGISTRANT_NAME,
    ((Current_Assets - Previous_Assets) / Previous_Assets * 100) as Growth_Percentage
FROM 
    AssetGrowth
WHERE 
    Previous_Assets IS NOT NULL
    AND Previous_Assets > 0
ORDER BY 
    Growth_Percentage DESC
LIMIT 10;

9. "Find any funds that seem to be taking on more risk lately? Look at their borrowing trends."
WITH BorrowingTrends AS (
    SELECT 
        F.SERIES_NAME,
        F.TOTAL_ASSETS,
        F.BORROWING_PAY_WITHIN_1YR,
        F.BORROWING_PAY_AFTER_1YR,
        CAST(F.BORROWING_PAY_WITHIN_1YR AS FLOAT) / NULLIF(CAST(F.TOTAL_ASSETS AS FLOAT), 0) * 100 as Short_Term_Borrow_Ratio,
        CAST(F.BORROWING_PAY_AFTER_1YR AS FLOAT) / NULLIF(CAST(F.TOTAL_ASSETS AS FLOAT), 0) * 100 as Long_Term_Borrow_Ratio
    FROM 
        FUND_REPORTED_INFO F
)
SELECT 
    SERIES_NAME,
    Short_Term_Borrow_Ratio,
    Long_Term_Borrow_Ratio,
    Short_Term_Borrow_Ratio + Long_Term_Borrow_Ratio as Total_Borrow_Ratio
FROM 
    BorrowingTrends
WHERE 
    Short_Term_Borrow_Ratio + Long_Term_Borrow_Ratio > 10
ORDER BY 
    Total_Borrow_Ratio DESC;

10. "Check which investment firms have the most diverse geographic exposure in their holdings"
WITH GeographicDiversity AS (
    SELECT 
        R.REGISTRANT_NAME,
        COUNT(DISTINCT H.INVESTMENT_COUNTRY) as Country_Count,
        COUNT(DISTINCT H.HOLDING_ID) as Total_Holdings
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
)
SELECT 
    REGISTRANT_NAME,
    Country_Count,
    Total_Holdings,
    ROUND(CAST(Country_Count AS FLOAT) / CAST(Total_Holdings AS FLOAT) * 100, 2) as Diversity_Score
FROM 
    GeographicDiversity
WHERE 
    Total_Holdings > 10
ORDER BY 
    Country_Count DESC
LIMIT 10;

11. "Could you check which funds have significantly changed their cash positions in the last quarter?"
WITH CashTrends AS (
    SELECT 
        F.SERIES_NAME,
        S.QUARTER,
        F.CASH_NOT_RPTD_IN_C_OR_D,
        F.TOTAL_ASSETS,
        CAST(F.CASH_NOT_RPTD_IN_C_OR_D AS FLOAT) / NULLIF(CAST(F.TOTAL_ASSETS AS FLOAT), 0) * 100 as Cash_Ratio
    FROM 
        FUND_REPORTED_INFO F
        JOIN SUBMISSION S ON F.ACCESSION_NUMBER = S.ACCESSION_NUMBER
)
SELECT 
    ct1.SERIES_NAME,
    ct1.Cash_Ratio as Current_Cash_Ratio,
    ct2.Cash_Ratio as Previous_Cash_Ratio,
    ct1.Cash_Ratio - ct2.Cash_Ratio as Change_In_Cash_Ratio
FROM 
    CashTrends ct1
    JOIN CashTrends ct2 
        ON ct1.SERIES_NAME = ct2.SERIES_NAME
        AND ct1.QUARTER > ct2.QUARTER
WHERE 
    ABS(ct1.Cash_Ratio - ct2.Cash_Ratio) > 5
ORDER BY 
    ABS(ct1.Cash_Ratio - ct2.Cash_Ratio) DESC;

12. "Find which investment styles are performing best this quarter? Like growth vs value funds?"
WITH StylePerformance AS (
    SELECT 
        CASE 
            WHEN F.SERIES_NAME LIKE '%GROWTH%' THEN 'Growth'
            WHEN F.SERIES_NAME LIKE '%VALUE%' THEN 'Value'
            WHEN F.SERIES_NAME LIKE '%BLEND%' THEN 'Blend'
            ELSE 'Other'
        END as Investment_Style,
        AVG(CAST(M.MONTHLY_TOTAL_RETURN1 AS FLOAT)) as Avg_Monthly_Return,
        COUNT(*) as Fund_Count
    FROM 
        FUND_REPORTED_INFO F
        JOIN MONTHLY_TOTAL_RETURN M 
            ON F.ACCESSION_NUMBER = M.ACCESSION_NUMBER
    GROUP BY 
        CASE 
            WHEN F.SERIES_NAME LIKE '%GROWTH%' THEN 'Growth'
            WHEN F.SERIES_NAME LIKE '%VALUE%' THEN 'Value'
            WHEN F.SERIES_NAME LIKE '%BLEND%' THEN 'Blend'
            ELSE 'Other'
        END
)
SELECT 
    Investment_Style,
    Avg_Monthly_Return,
    Fund_Count
FROM 
    StylePerformance
WHERE 
    Investment_Style != 'Other'
ORDER BY 
    Avg_Monthly_Return DESC;

13. "Find me funds that might be too exposed to interest rate changes - check their duration risk"
WITH InterestRateExposure AS (
    SELECT 
        F.SERIES_NAME,
        IR.INTRST_RATE_CHANGE_10YR_DV01,
        IR.INTRST_RATE_CHANGE_30YR_DV01,
        F.TOTAL_ASSETS
    FROM 
        FUND_REPORTED_INFO F
        JOIN INTEREST_RATE_RISK IR 
            ON F.ACCESSION_NUMBER = IR.ACCESSION_NUMBER
    WHERE 
        IR.INTRST_RATE_CHANGE_10YR_DV01 IS NOT NULL
)
SELECT 
    SERIES_NAME,
    CAST(INTRST_RATE_CHANGE_10YR_DV01 AS FLOAT) as Ten_Year_Risk,
    CAST(INTRST_RATE_CHANGE_30YR_DV01 AS FLOAT) as Thirty_Year_Risk
FROM 
    InterestRateExposure
WHERE 
    CAST(INTRST_RATE_CHANGE_10YR_DV01 AS FLOAT) > 1.0
    OR CAST(INTRST_RATE_CHANGE_30YR_DV01 AS FLOAT) > 1.0
ORDER BY 
    Ten_Year_Risk DESC;

14. "I need to find funds with strong and consistent returns over all three months"
WITH ConsistentPerformers AS (
    SELECT 
        F.SERIES_NAME,
        M.MONTHLY_TOTAL_RETURN1,
        M.MONTHLY_TOTAL_RETURN2,
        M.MONTHLY_TOTAL_RETURN3,
        (CAST(M.MONTHLY_TOTAL_RETURN1 AS FLOAT) + 
         CAST(M.MONTHLY_TOTAL_RETURN2 AS FLOAT) + 
         CAST(M.MONTHLY_TOTAL_RETURN3 AS FLOAT)) / 3 as Avg_Return
    FROM 
        FUND_REPORTED_INFO F
        JOIN MONTHLY_TOTAL_RETURN M 
            ON F.ACCESSION_NUMBER = M.ACCESSION_NUMBER
    WHERE 
        M.MONTHLY_TOTAL_RETURN1 IS NOT NULL
        AND M.MONTHLY_TOTAL_RETURN2 IS NOT NULL
        AND M.MONTHLY_TOTAL_RETURN3 IS NOT NULL
)
SELECT 
    SERIES_NAME,
    MONTHLY_TOTAL_RETURN1,
    MONTHLY_TOTAL_RETURN2,
    MONTHLY_TOTAL_RETURN3,
    Avg_Return
FROM 
    ConsistentPerformers
WHERE 
    CAST(MONTHLY_TOTAL_RETURN1 AS FLOAT) > 0
    AND CAST(MONTHLY_TOTAL_RETURN2 AS FLOAT) > 0
    AND CAST(MONTHLY_TOTAL_RETURN3 AS FLOAT) > 0
ORDER BY 
    Avg_Return DESC
LIMIT 10;

15. "Which funds have the most foreign currency exposure? Especially interested in emerging markets"
WITH CurrencyExposure AS (
    SELECT 
        F.SERIES_NAME,
        COUNT(DISTINCT H.CURRENCY_CODE) as Currency_Count,
        SUM(CASE 
            WHEN H.CURRENCY_CODE NOT IN ('USD', 'EUR', 'GBP', 'JPY', 'CHF') 
            THEN CAST(H.CURRENCY_VALUE AS FLOAT) 
            ELSE 0 
        END) as Emerging_Market_Exposure
    FROM 
        FUND_REPORTED_INFO F
        JOIN FUND_REPORTED_HOLDING H 
            ON F.ACCESSION_NUMBER = H.ACCESSION_NUMBER
    WHERE 
        H.CURRENCY_CODE IS NOT NULL
    GROUP BY 
        F.SERIES_NAME
)
SELECT 
    SERIES_NAME,
    Currency_Count,
    Emerging_Market_Exposure
FROM 
    CurrencyExposure
WHERE 
    Currency_Count > 3
ORDER BY 
    Emerging_Market_Exposure DESC
LIMIT 15;

16. "Show me which asset categories had the best returns last month?"
WITH CategoryReturns AS (
    SELECT 
        H.ASSET_CAT,
        AVG(CAST(M.MONTHLY_TOTAL_RETURN1 AS FLOAT)) as Avg_Return,
        COUNT(DISTINCT F.SERIES_NAME) as Fund_Count
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
)
SELECT 
    ASSET_CAT,
    Avg_Return,
    Fund_Count
FROM 
    CategoryReturns
WHERE 
    Fund_Count > 5
ORDER BY 
    Avg_Return DESC;

17. "Find me funds that might be taking on too much credit risk - look at their non-investment grade holdings"
WITH CreditRiskExposure AS (
    SELECT 
        F.SERIES_NAME,
        SUM(CAST(F.CREDIT_SPREAD_10YR_NONINVEST AS FLOAT)) as NonInvest_Exposure,
        SUM(CAST(F.CREDIT_SPREAD_10YR_INVEST AS FLOAT)) as Invest_Exposure,
        F.TOTAL_ASSETS
    FROM 
        FUND_REPORTED_INFO F
    WHERE 
        F.CREDIT_SPREAD_10YR_NONINVEST IS NOT NULL
    GROUP BY 
        F.SERIES_NAME,
        F.TOTAL_ASSETS
)
SELECT 
    SERIES_NAME,
    NonInvest_Exposure / NULLIF(CAST(TOTAL_ASSETS AS FLOAT), 0) * 100 as NonInvest_Percentage
FROM 
    CreditRiskExposure
WHERE 
    NonInvest_Exposure > Invest_Exposure
ORDER BY 
    NonInvest_Percentage DESC;

18. "Which registrants have the most diverse mix of fund types in their lineup?"
WITH FundTypes AS (
    SELECT 
        R.REGISTRANT_NAME,
        COUNT(DISTINCT 
            CASE 
                WHEN F.SERIES_NAME LIKE '%BOND%' THEN 'BOND'
                WHEN F.SERIES_NAME LIKE '%EQUITY%' THEN 'EQUITY'
                WHEN F.SERIES_NAME LIKE '%ETF%' THEN 'ETF'
                WHEN F.SERIES_NAME LIKE '%INDEX%' THEN 'INDEX'
                WHEN F.SERIES_NAME LIKE '%MONEY MARKET%' THEN 'MONEY MARKET'
                WHEN F.SERIES_NAME LIKE '%BALANCED%' THEN 'BALANCED'
                ELSE 'OTHER'
            END
        ) as Fund_Type_Count,
        COUNT(*) as Total_Funds
    FROM 
        REGISTRANT R
        JOIN FUND_REPORTED_INFO F 
            ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
    GROUP BY 
        R.REGISTRANT_NAME
)
SELECT 
    REGISTRANT_NAME,
    Fund_Type_Count,
    Total_Funds,
    (Fund_Type_Count * 100.0 / Total_Funds) as Diversity_Score
FROM 
    FundTypes
WHERE 
    Total_Funds >= 5
ORDER BY 
    Fund_Type_Count DESC, Total_Funds DESC;

19. "Could you identify funds that might be style drifting? Check their recent holdings changes"
WITH HoldingChanges AS (
    SELECT 
        F.SERIES_NAME,
        S.QUARTER,
        COUNT(CASE WHEN H.ASSET_CAT LIKE '%EQUITY%' THEN 1 END) * 100.0 / COUNT(*) as Equity_Percentage,
        COUNT(CASE WHEN H.ASSET_CAT LIKE '%DEBT%' THEN 1 END) * 100.0 / COUNT(*) as Debt_Percentage
    FROM 
        FUND_REPORTED_INFO F
        JOIN FUND_REPORTED_HOLDING H 
            ON F.ACCESSION_NUMBER = H.ACCESSION_NUMBER
        JOIN SUBMISSION S 
            ON F.ACCESSION_NUMBER = S.ACCESSION_NUMBER
    GROUP BY 
        F.SERIES_NAME,
        S.QUARTER
)
SELECT 
    h1.SERIES_NAME,
    h1.Equity_Percentage - h2.Equity_Percentage as Equity_Change,
    h1.Debt_Percentage - h2.Debt_Percentage as Debt_Change
FROM 
    HoldingChanges h1
    JOIN HoldingChanges h2 
        ON h1.SERIES_NAME = h2.SERIES_NAME
        AND h1.QUARTER > h2.QUARTER
WHERE 
    ABS(h1.Equity_Percentage - h2.Equity_Percentage) > 10
    OR ABS(h1.Debt_Percentage - h2.Debt_Percentage) > 10
ORDER BY 
    ABS(h1.Equity_Percentage - h2.Equity_Percentage) DESC;

20. "Show me the funds with the highest quality fixed income portfolios"
WITH BondQuality AS (
    SELECT 
        F.SERIES_NAME,
        F.TOTAL_ASSETS,
        F.CREDIT_SPREAD_10YR_INVEST,
        F.CREDIT_SPREAD_10YR_NONINVEST,
        CAST(F.CREDIT_SPREAD_10YR_INVEST AS FLOAT) / 
        NULLIF(CAST(F.CREDIT_SPREAD_10YR_INVEST AS FLOAT) + 
               CAST(F.CREDIT_SPREAD_10YR_NONINVEST AS FLOAT), 0) * 100 as Investment_Grade_Ratio
    FROM 
        FUND_REPORTED_INFO F
    WHERE 
        F.SERIES_NAME LIKE '%BOND%'
        OR F.SERIES_NAME LIKE '%FIXED INCOME%'
)
SELECT 
    SERIES_NAME,
    Investment_Grade_Ratio,
    TOTAL_ASSETS
FROM 
    BondQuality
WHERE 
    Investment_Grade_Ratio > 80
ORDER BY 
    Investment_Grade_Ratio DESC
LIMIT 15;

21. "How have the largest funds performed compared to smaller ones this quarter?"
WITH FundSizePerformance AS (
    SELECT 
        F.SERIES_NAME,
        CAST(F.TOTAL_ASSETS AS FLOAT) as Assets,
        CAST(M.MONTHLY_TOTAL_RETURN1 AS FLOAT) as Latest_Return,
        NTILE(4) OVER (ORDER BY CAST(F.TOTAL_ASSETS AS FLOAT)) as Size_Quartile
    FROM 
        FUND_REPORTED_INFO F
        JOIN MONTHLY_TOTAL_RETURN M 
            ON F.ACCESSION_NUMBER = M.ACCESSION_NUMBER
    WHERE 
        F.TOTAL_ASSETS IS NOT NULL
        AND M.MONTHLY_TOTAL_RETURN1 IS NOT NULL
)
SELECT 
    Size_Quartile,
    AVG(Latest_Return) as Avg_Return,
    COUNT(*) as Fund_Count,
    AVG(Assets) as Avg_Assets
FROM 
    FundSizePerformance
GROUP BY 
    Size_Quartile
ORDER BY 
    Size_Quartile;

22. "Looking for funds that might have liquidity issues - check their cash versus short-term obligations"
WITH LiquidityAnalysis AS (
    SELECT 
        F.SERIES_NAME,
        CAST(F.CASH_NOT_RPTD_IN_C_OR_D AS FLOAT) as Cash,
        CAST(F.BORROWING_PAY_WITHIN_1YR AS FLOAT) as Short_Term_Obligations,
        CAST(F.TOTAL_ASSETS AS FLOAT) as Total_Assets
    FROM 
        FUND_REPORTED_INFO F
    WHERE 
        F.CASH_NOT_RPTD_IN_C_OR_D IS NOT NULL
)
SELECT 
    SERIES_NAME,
    Cash / NULLIF(Short_Term_Obligations, 0) as Cash_Coverage_Ratio,
    Cash / Total_Assets * 100 as Cash_Percentage
FROM 
    LiquidityAnalysis
WHERE 
    Short_Term_Obligations > 0
ORDER BY 
    Cash_Coverage_Ratio ASC
LIMIT 15;

23. "Which investment companies are most exposed to international markets?"
WITH InternationalExposure AS (
    SELECT 
        R.REGISTRANT_NAME,
        COUNT(CASE WHEN H.INVESTMENT_COUNTRY != 'US' THEN 1 END) as International_Holdings,
        COUNT(*) as Total_Holdings,
        SUM(CASE WHEN H.INVESTMENT_COUNTRY != 'US' 
            THEN CAST(H.CURRENCY_VALUE AS FLOAT) ELSE 0 END) as International_Value
    FROM 
        REGISTRANT R
        JOIN FUND_REPORTED_INFO F 
            ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
        JOIN FUND_REPORTED_HOLDING H 
            ON F.ACCESSION_NUMBER = H.ACCESSION_NUMBER
    GROUP BY 
        R.REGISTRANT_NAME
)
SELECT 
    REGISTRANT_NAME,
    International_Holdings * 100.0 / NULLIF(Total_Holdings, 0) as International_Percentage,
    International_Value
FROM 
    InternationalExposure
WHERE 
    Total_Holdings > 10
ORDER BY 
    International_Percentage DESC
LIMIT 10;

24. "Locate funds that have dramatically changed their asset mix recently?"
WITH AssetMixChange AS (
    SELECT 
        F.SERIES_NAME,
        S.QUARTER,
        SUM(CASE WHEN H.ASSET_CAT LIKE '%EQUITY%' 
            THEN CAST(H.CURRENCY_VALUE AS FLOAT) ELSE 0 END) / 
            NULLIF(CAST(F.TOTAL_ASSETS AS FLOAT), 0) * 100 as Equity_Percentage
    FROM 
        FUND_REPORTED_INFO F
        JOIN FUND_REPORTED_HOLDING H 
            ON F.ACCESSION_NUMBER = H.ACCESSION_NUMBER
        JOIN SUBMISSION S 
            ON F.ACCESSION_NUMBER = S.ACCESSION_NUMBER
    GROUP BY 
        F.SERIES_NAME,
        S.QUARTER,
        F.TOTAL_ASSETS
)
SELECT 
    a1.SERIES_NAME,
    a1.Equity_Percentage as Current_Equity_Pct,
    a2.Equity_Percentage as Previous_Equity_Pct,
    a1.Equity_Percentage - a2.Equity_Percentage as Equity_Change
FROM 
    AssetMixChange a1
    JOIN AssetMixChange a2 
        ON a1.SERIES_NAME = a2.SERIES_NAME 
        AND a1.QUARTER > a2.QUARTER
WHERE 
    ABS(a1.Equity_Percentage - a2.Equity_Percentage) > 15
ORDER BY 
    ABS(a1.Equity_Percentage - a2.Equity_Percentage) DESC;

25. "Find the funds with the most consistent monthly returns - looking for low volatility"
WITH ReturnVolatility AS (
    SELECT 
        F.SERIES_NAME,
        CAST(M.MONTHLY_TOTAL_RETURN1 AS FLOAT) as Return1,
        CAST(M.MONTHLY_TOTAL_RETURN2 AS FLOAT) as Return2,
        CAST(M.MONTHLY_TOTAL_RETURN3 AS FLOAT) as Return3,
        STDDEV(CAST(M.MONTHLY_TOTAL_RETURN1 AS FLOAT)) OVER (
            PARTITION BY F.SERIES_NAME
        ) as Return_StdDev
    FROM 
        FUND_REPORTED_INFO F
        JOIN MONTHLY_TOTAL_RETURN M 
            ON F.ACCESSION_NUMBER = M.ACCESSION_NUMBER
    WHERE 
        M.MONTHLY_TOTAL_RETURN1 IS NOT NULL 
        AND M.MONTHLY_TOTAL_RETURN2 IS NOT NULL 
        AND M.MONTHLY_TOTAL_RETURN3 IS NOT NULL
)
SELECT 
    SERIES_NAME,
    Return_StdDev,
    (Return1 + Return2 + Return3) / 3 as Avg_Return
FROM 
    ReturnVolatility
WHERE 
    Return_StdDev IS NOT NULL
ORDER BY 
    Return_StdDev ASC
LIMIT 15;

26. "Show me which funds are heavily invested in derivative instruments"
WITH DerivativeExposure AS (
    SELECT 
        F.SERIES_NAME,
        COUNT(DISTINCT OD.HOLDING_ID) as Derivative_Count,
        SUM(CAST(H.CURRENCY_VALUE AS FLOAT)) as Derivative_Value,
        CAST(F.TOTAL_ASSETS AS FLOAT) as Total_Assets
    FROM 
        FUND_REPORTED_INFO F
        JOIN FUND_REPORTED_HOLDING H 
            ON F.ACCESSION_NUMBER = H.ACCESSION_NUMBER
        JOIN OTHER_DERIV OD 
            ON H.HOLDING_ID = OD.HOLDING_ID
    GROUP BY 
        F.SERIES_NAME,
        F.TOTAL_ASSETS
)
SELECT 
    SERIES_NAME,
    Derivative_Count,
    (Derivative_Value / Total_Assets * 100) as Derivative_Percentage
FROM 
    DerivativeExposure
WHERE 
    Total_Assets > 0
ORDER BY 
    Derivative_Percentage DESC
LIMIT 10;

27. "Help me find funds that might be too concentrated in specific sectors"
WITH SectorConcentration AS (
    SELECT 
        F.SERIES_NAME,
        H.ASSET_CAT,
        COUNT(*) as Holdings_Count,
        SUM(CAST(H.CURRENCY_VALUE AS FLOAT)) as Sector_Value,
        CAST(F.TOTAL_ASSETS AS FLOAT) as Total_Assets
    FROM 
        FUND_REPORTED_INFO F
        JOIN FUND_REPORTED_HOLDING H 
            ON F.ACCESSION_NUMBER = H.ACCESSION_NUMBER
    WHERE 
        H.ASSET_CAT IS NOT NULL
    GROUP BY 
        F.SERIES_NAME,
        H.ASSET_CAT,
        F.TOTAL_ASSETS
)
SELECT 
    SERIES_NAME,
    ASSET_CAT,
    (Sector_Value / Total_Assets * 100) as Sector_Percentage
FROM 
    SectorConcentration
WHERE 
    (Sector_Value / Total_Assets * 100) > 30
ORDER BY 
    Sector_Percentage DESC;

28. "Which funds seem to be shifting towards safer assets lately?"
WITH AssetSafetyTrend AS (
    SELECT 
        F.SERIES_NAME,
        S.QUARTER,
        SUM(CASE 
            WHEN H.ASSET_CAT IN ('GOVT', 'TREASURY', 'CASH') 
            THEN CAST(H.CURRENCY_VALUE AS FLOAT) 
            ELSE 0 
        END) / NULLIF(CAST(F.TOTAL_ASSETS AS FLOAT), 0) * 100 as Safe_Asset_Percentage
    FROM 
        FUND_REPORTED_INFO F
        JOIN FUND_REPORTED_HOLDING H 
            ON F.ACCESSION_NUMBER = H.ACCESSION_NUMBER
        JOIN SUBMISSION S 
            ON F.ACCESSION_NUMBER = S.ACCESSION_NUMBER
    GROUP BY 
        F.SERIES_NAME,
        S.QUARTER,
        F.TOTAL_ASSETS
)
SELECT 
    a1.SERIES_NAME,
    a1.Safe_Asset_Percentage as Current_Safe_Pct,
    a2.Safe_Asset_Percentage as Previous_Safe_Pct,
    a1.Safe_Asset_Percentage - a2.Safe_Asset_Percentage as Safety_Shift
FROM 
    AssetSafetyTrend a1
    JOIN AssetSafetyTrend a2 
        ON a1.SERIES_NAME = a2.SERIES_NAME
        AND a1.QUARTER > a2.QUARTER
WHERE 
    a1.Safe_Asset_Percentage - a2.Safe_Asset_Percentage > 10
ORDER BY 
    Safety_Shift DESC;

29. "Find funds with the highest quality fixed-income holdings"
WITH FixedIncomeQuality AS (
    SELECT 
        F.SERIES_NAME,
        SUM(CAST(F.CREDIT_SPREAD_10YR_INVEST AS FLOAT)) as Investment_Grade_Exposure,
        SUM(CAST(F.CREDIT_SPREAD_10YR_NONINVEST AS FLOAT)) as NonInvestment_Grade_Exposure,
        CAST(F.TOTAL_ASSETS AS FLOAT) as Total_Assets
    FROM 
        FUND_REPORTED_INFO F
    WHERE 
        F.SERIES_NAME LIKE '%BOND%'
        OR F.SERIES_NAME LIKE '%FIXED INCOME%'
    GROUP BY 
        F.SERIES_NAME,
        F.TOTAL_ASSETS
)
SELECT 
    SERIES_NAME,
    (Investment_Grade_Exposure / NULLIF(Investment_Grade_Exposure + NonInvestment_Grade_Exposure, 0) * 100) as Quality_Score
FROM 
    FixedIncomeQuality
WHERE 
    Investment_Grade_Exposure + NonInvestment_Grade_Exposure > 0
ORDER BY 
    Quality_Score DESC
LIMIT 15;

30. "Which funds are taking on the most interest rate risk?"
WITH InterestRateRisk AS (
    SELECT 
        F.SERIES_NAME,
        IR.INTRST_RATE_CHANGE_10YR_DV01,
        IR.INTRST_RATE_CHANGE_30YR_DV01,
        F.TOTAL_ASSETS
    FROM 
        FUND_REPORTED_INFO F
        JOIN INTEREST_RATE_RISK IR 
            ON F.ACCESSION_NUMBER = IR.ACCESSION_NUMBER
    WHERE 
        IR.INTRST_RATE_CHANGE_10YR_DV01 IS NOT NULL
        OR IR.INTRST_RATE_CHANGE_30YR_DV01 IS NOT NULL
)
SELECT 
    SERIES_NAME,
    CAST(INTRST_RATE_CHANGE_10YR_DV01 AS FLOAT) as Ten_Year_Risk,
    CAST(INTRST_RATE_CHANGE_30YR_DV01 AS FLOAT) as Thirty_Year_Risk,
    CAST(INTRST_RATE_CHANGE_10YR_DV01 AS FLOAT) + CAST(INTRST_RATE_CHANGE_30YR_DV01 AS FLOAT) as Total_Risk
FROM 
    InterestRateRisk
ORDER BY 
    Total_Risk DESC
LIMIT 10;

31. "Identify funds with high portfolio turnover based on their trading activity?"
WITH TradingActivity AS (
    SELECT 
        F.SERIES_NAME,
        SUM(CAST(F.SALES_FLOW_MON1 AS FLOAT) + 
            CAST(F.SALES_FLOW_MON2 AS FLOAT) + 
            CAST(F.SALES_FLOW_MON3 AS FLOAT)) as Total_Sales,
        CAST(F.TOTAL_ASSETS AS FLOAT) as Assets
    FROM 
        FUND_REPORTED_INFO F
    WHERE 
        F.SALES_FLOW_MON1 IS NOT NULL 
        AND F.SALES_FLOW_MON2 IS NOT NULL 
        AND F.SALES_FLOW_MON3 IS NOT NULL
    GROUP BY 
        F.SERIES_NAME,
        F.TOTAL_ASSETS
)
SELECT 
    SERIES_NAME,
    (Total_Sales / NULLIF(Assets, 0)) * 100 as Turnover_Rate
FROM 
    TradingActivity
WHERE 
    Assets > 0
ORDER BY 
    Turnover_Rate DESC
LIMIT 15;

32. "Which funds have the best risk-adjusted returns? Look at return consistency and magnitude."
WITH RiskAdjusted AS (
    SELECT 
        F.SERIES_NAME,
        AVG(CAST(M.MONTHLY_TOTAL_RETURN1 AS FLOAT)) as Avg_Return,
        STDDEV(CAST(M.MONTHLY_TOTAL_RETURN1 AS FLOAT)) as Return_StdDev,
        COUNT(*) as Months_Reported
    FROM 
        FUND_REPORTED_INFO F
        JOIN MONTHLY_TOTAL_RETURN M 
            ON F.ACCESSION_NUMBER = M.ACCESSION_NUMBER
    GROUP BY 
        F.SERIES_NAME
    HAVING 
        COUNT(*) >= 3
)
SELECT 
    SERIES_NAME,
    Avg_Return,
    Return_StdDev,
    CASE 
        WHEN Return_StdDev = 0 THEN NULL 
        ELSE Avg_Return / Return_StdDev 
    END as Sharpe_Ratio
FROM 
    RiskAdjusted
WHERE 
    Return_StdDev > 0
ORDER BY 
    Sharpe_Ratio DESC
LIMIT 10;

33. "Show me funds with heavy geographic concentration in emerging markets"
WITH GeographicConcentration AS (
    SELECT 
        F.SERIES_NAME,
        H.INVESTMENT_COUNTRY,
        COUNT(*) as Holdings_Count,
        SUM(CAST(H.CURRENCY_VALUE AS FLOAT)) as Country_Value,
        CAST(F.TOTAL_ASSETS AS FLOAT) as Total_Assets
    FROM 
        FUND_REPORTED_INFO F
        JOIN FUND_REPORTED_HOLDING H 
            ON F.ACCESSION_NUMBER = H.ACCESSION_NUMBER
    WHERE 
        H.INVESTMENT_COUNTRY NOT IN ('US', 'GB', 'FR', 'DE', 'JP', 'CA')
        AND H.INVESTMENT_COUNTRY IS NOT NULL
    GROUP BY 
        F.SERIES_NAME,
        H.INVESTMENT_COUNTRY,
        F.TOTAL_ASSETS
)
SELECT 
    SERIES_NAME,
    INVESTMENT_COUNTRY,
    (Country_Value / Total_Assets * 100) as Country_Percentage
FROM 
    GeographicConcentration
WHERE 
    (Country_Value / Total_Assets * 100) > 15
ORDER BY 
    Country_Percentage DESC;

34. "Help me find funds that look like they're changing their investment strategy"
WITH StrategyShift AS (
    SELECT 
        F.SERIES_NAME,
        S.QUARTER,
        SUM(CASE 
            WHEN H.ASSET_CAT LIKE '%EQUITY%' THEN CAST(H.CURRENCY_VALUE AS FLOAT)
            ELSE 0 
        END) / NULLIF(CAST(F.TOTAL_ASSETS AS FLOAT), 0) * 100 as Equity_Pct,
        SUM(CASE 
            WHEN H.ASSET_CAT LIKE '%DEBT%' THEN CAST(H.CURRENCY_VALUE AS FLOAT)
            ELSE 0 
        END) / NULLIF(CAST(F.TOTAL_ASSETS AS FLOAT), 0) * 100 as Debt_Pct
    FROM 
        FUND_REPORTED_INFO F
        JOIN FUND_REPORTED_HOLDING H 
            ON F.ACCESSION_NUMBER = H.ACCESSION_NUMBER
        JOIN SUBMISSION S 
            ON F.ACCESSION_NUMBER = S.ACCESSION_NUMBER
    GROUP BY 
        F.SERIES_NAME,
        S.QUARTER,
        F.TOTAL_ASSETS
)
SELECT 
    s1.SERIES_NAME,
    s1.Equity_Pct - s2.Equity_Pct as Equity_Shift,
    s1.Debt_Pct - s2.Debt_Pct as Debt_Shift
FROM 
    StrategyShift s1
    JOIN StrategyShift s2 
        ON s1.SERIES_NAME = s2.SERIES_NAME
        AND s1.QUARTER > s2.QUARTER
WHERE 
    ABS(s1.Equity_Pct - s2.Equity_Pct) > 10
    OR ABS(s1.Debt_Pct - s2.Debt_Pct) > 10
ORDER BY 
    ABS(s1.Equity_Pct - s2.Equity_Pct) + ABS(s1.Debt_Pct - s2.Debt_Pct) DESC;

35. "Let's see which fund families are most active in securities lending"
WITH LendingActivity AS (
    SELECT 
        R.REGISTRANT_NAME,
        COUNT(DISTINCT F.SERIES_NAME) as Total_Funds,
        COUNT(DISTINCT CASE 
            WHEN SL.IS_LOAN_BY_FUND = 'Y' 
            THEN F.SERIES_NAME 
        END) as Lending_Funds
    FROM 
        REGISTRANT R
        JOIN FUND_REPORTED_INFO F 
            ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
        LEFT JOIN SECURITIES_LENDING SL 
            ON F.ACCESSION_NUMBER = SL.HOLDING_ID
    GROUP BY 
        R.REGISTRANT_NAME
)
SELECT 
    REGISTRANT_NAME,
    Lending_Funds,
    Total_Funds,
    (Lending_Funds * 100.0 / Total_Funds) as Lending_Percentage
FROM 
    LendingActivity
WHERE 
    Total_Funds >= 5
ORDER BY 
    Lending_Percentage DESC
LIMIT 15;

36. "Find funds that might be too leveraged through their borrowing activities"
WITH LeverageAnalysis AS (
    SELECT 
        F.SERIES_NAME,
        CAST(F.BORROWING_PAY_WITHIN_1YR AS FLOAT) +
        CAST(F.BORROWING_PAY_AFTER_1YR AS FLOAT) as Total_Borrowing,
        CAST(F.TOTAL_ASSETS AS FLOAT) as Total_Assets
    FROM 
        FUND_REPORTED_INFO F
    WHERE 
        F.BORROWING_PAY_WITHIN_1YR IS NOT NULL
        AND F.BORROWING_PAY_AFTER_1YR IS NOT NULL
)
SELECT 
    SERIES_NAME,
    (Total_Borrowing / NULLIF(Total_Assets, 0) * 100) as Leverage_Ratio
FROM 
    LeverageAnalysis
WHERE 
    Total_Assets > 0
ORDER BY 
    Leverage_Ratio DESC
LIMIT 10;

37. "Which funds are most active in derivative trading across different types?"
WITH DerivativeActivity AS (
    SELECT 
        F.SERIES_NAME,
        COUNT(DISTINCT CASE 
            WHEN FFN.HOLDING_ID IS NOT NULL THEN 'FUTURES_FORWARDS'
            WHEN SW.HOLDING_ID IS NOT NULL THEN 'SWAPS'
            WHEN OD.HOLDING_ID IS NOT NULL THEN 'OTHER_DERIVATIVES'
        END) as Derivative_Types_Used,
        COUNT(*) as Total_Derivative_Positions
    FROM 
        FUND_REPORTED_INFO F
        LEFT JOIN FUT_FWD_NONFOREIGNCUR_CONTRACT FFN 
            ON F.ACCESSION_NUMBER = FFN.HOLDING_ID
        LEFT JOIN NONFOREIGN_EXCHANGE_SWAP SW 
            ON F.ACCESSION_NUMBER = SW.HOLDING_ID
        LEFT JOIN OTHER_DERIV OD 
            ON F.ACCESSION_NUMBER = OD.HOLDING_ID
    GROUP BY 
        F.SERIES_NAME
)
SELECT 
    SERIES_NAME,
    Derivative_Types_Used,
    Total_Derivative_Positions
FROM 
    DerivativeActivity
WHERE 
    Derivative_Types_Used > 0
ORDER BY 
    Derivative_Types_Used DESC, 
    Total_Derivative_Positions DESC;

38. "Check for funds with significant counterparty exposure through their derivatives"
WITH CounterpartyRisk AS (
    SELECT 
        F.SERIES_NAME,
        DC.DERIVATIVE_COUNTERPARTY_NAME,
        COUNT(*) as Transaction_Count,
        COUNT(DISTINCT DC.HOLDING_ID) as Unique_Positions
    FROM 
        FUND_REPORTED_INFO F
        JOIN FUND_REPORTED_HOLDING H 
            ON F.ACCESSION_NUMBER = H.ACCESSION_NUMBER
        JOIN DERIVATIVE_COUNTERPARTY DC 
            ON H.HOLDING_ID = DC.HOLDING_ID
    GROUP BY 
        F.SERIES_NAME,
        DC.DERIVATIVE_COUNTERPARTY_NAME
)
SELECT 
    SERIES_NAME,
    DERIVATIVE_COUNTERPARTY_NAME,
    Transaction_Count,
    Unique_Positions
FROM 
    CounterpartyRisk
ORDER BY 
    Transaction_Count DESC
LIMIT 15;

39. "Find funds with unusual monthly return patterns - looking for potential outliers"
WITH ReturnPatterns AS (
    SELECT 
        F.SERIES_NAME,
        CAST(M.MONTHLY_TOTAL_RETURN1 AS FLOAT) as Return1,
        CAST(M.MONTHLY_TOTAL_RETURN2 AS FLOAT) as Return2,
        CAST(M.MONTHLY_TOTAL_RETURN3 AS FLOAT) as Return3,
        ABS(CAST(M.MONTHLY_TOTAL_RETURN1 AS FLOAT) - 
            (CAST(M.MONTHLY_TOTAL_RETURN2 AS FLOAT) + 
             CAST(M.MONTHLY_TOTAL_RETURN3 AS FLOAT)) / 2) as Return_Deviation
    FROM 
        FUND_REPORTED_INFO F
        JOIN MONTHLY_TOTAL_RETURN M 
            ON F.ACCESSION_NUMBER = M.ACCESSION_NUMBER
    WHERE 
        M.MONTHLY_TOTAL_RETURN1 IS NOT NULL
        AND M.MONTHLY_TOTAL_RETURN2 IS NOT NULL
        AND M.MONTHLY_TOTAL_RETURN3 IS NOT NULL
)
SELECT 
    SERIES_NAME,
    Return1,
    Return2,
    Return3,
    Return_Deviation
FROM 
    ReturnPatterns
WHERE 
    Return_Deviation > 5
ORDER BY 
    Return_Deviation DESC;

40. "Show me which funds have the most diverse debt security holdings by maturity"
WITH MaturityDiversity AS (
    SELECT 
        F.SERIES_NAME,
        COUNT(DISTINCT 
            CASE 
                WHEN DS.MATURITY_DATE <= DATE('now', '+1 year') THEN 'SHORT_TERM'
                WHEN DS.MATURITY_DATE <= DATE('now', '+5 year') THEN 'MEDIUM_TERM'
                ELSE 'LONG_TERM'
            END
        ) as Maturity_Types,
        COUNT(*) as Total_Debt_Securities
    FROM 
        FUND_REPORTED_INFO F
        JOIN FUND_REPORTED_HOLDING H 
            ON F.ACCESSION_NUMBER = H.ACCESSION_NUMBER
        JOIN DEBT_SECURITY DS 
            ON H.HOLDING_ID = DS.HOLDING_ID
    WHERE 
        DS.MATURITY_DATE IS NOT NULL
    GROUP BY 
        F.SERIES_NAME
)
SELECT 
    SERIES_NAME,
    Maturity_Types,
    Total_Debt_Securities,
    (Maturity_Types * 100.0 / 3) as Diversity_Score
FROM 
    MaturityDiversity
WHERE 
    Total_Debt_Securities >= 5
ORDER BY 
    Maturity_Types DESC, 
    Total_Debt_Securities DESC;
```
"""

gpt_queries_hard ="""
```
1. "Can you flag any worrying funds that have liabilities over half their assets? That's a bit of a red flag."
SELECT 
    F.SERIES_NAME,
    CAST(F.TOTAL_LIABILITIES AS FLOAT) / NULLIF(CAST(F.TOTAL_ASSETS AS FLOAT), 0) * 100 as Liability_Percentage,
    F.TOTAL_ASSETS,
    F.TOTAL_LIABILITIES
FROM 
    FUND_REPORTED_INFO F
WHERE 
    CAST(F.TOTAL_LIABILITIES AS FLOAT) / NULLIF(CAST(F.TOTAL_ASSETS AS FLOAT), 0) > 0.5
ORDER BY 
    Liability_Percentage DESC;

2. "I need to check for concentration risk - show me any holdings that are the biggest position in their funds."
WITH HoldingPercentages AS (
    SELECT 
        F.SERIES_NAME,
        H.ISSUER_NAME,
        H.PERCENTAGE,
        ROW_NUMBER() OVER (PARTITION BY F.SERIES_NAME ORDER BY CAST(H.PERCENTAGE AS FLOAT) DESC) as Position_Rank
    FROM 
        FUND_REPORTED_INFO F
        JOIN FUND_REPORTED_HOLDING H 
            ON F.ACCESSION_NUMBER = H.ACCESSION_NUMBER
    WHERE 
        H.PERCENTAGE IS NOT NULL
)
SELECT 
    SERIES_NAME,
    ISSUER_NAME,
    PERCENTAGE
FROM 
    HoldingPercentages
WHERE 
    Position_Rank = 1
ORDER BY 
    CAST(PERCENTAGE AS FLOAT) DESC;

3. "With rates being so volatile, which USD funds are most exposed to interest rate changes?"
SELECT 
    F.SERIES_NAME,
    IR.INTRST_RATE_CHANGE_10YR_DV01 as Ten_Year_Risk,
    IR.INTRST_RATE_CHANGE_30YR_DV01 as Thirty_Year_Risk,
    F.TOTAL_ASSETS
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
    CAST(IR.INTRST_RATE_CHANGE_10YR_DV01 AS FLOAT) DESC;

4. "Which funds are growing the fastest? Looking for top 5 by net asset growth between quarters."
WITH QuarterlyGrowth AS (
    SELECT 
        F1.SERIES_NAME,
        F1.QUARTER as Previous_Quarter,
        F2.QUARTER as Current_Quarter,
        CAST(F1.NET_ASSETS AS FLOAT) as Previous_Assets,
        CAST(F2.NET_ASSETS AS FLOAT) as Current_Assets,
        ((CAST(F2.NET_ASSETS AS FLOAT) - CAST(F1.NET_ASSETS AS FLOAT)) / 
         NULLIF(CAST(F1.NET_ASSETS AS FLOAT), 0)) * 100 as Growth_Percentage
    FROM 
        FUND_REPORTED_INFO F1
        JOIN FUND_REPORTED_INFO F2 
            ON F1.SERIES_ID = F2.SERIES_ID
            AND F1.QUARTER < F2.QUARTER
)
SELECT 
    SERIES_NAME,
    Previous_Quarter,
    Current_Quarter,
    Growth_Percentage,
    Current_Assets - Previous_Assets as Absolute_Growth
FROM 
    QuarterlyGrowth
ORDER BY 
    Growth_Percentage DESC
LIMIT 5;

5. "Looking for potential currency mismatches - any holdings where the currency doesn't match the country of investment?"
WITH CurrencyMismatches AS (
    SELECT 
        F.SERIES_NAME,
        H.ISSUER_NAME,
        H.CURRENCY_CODE,
        H.INVESTMENT_COUNTRY,
        H.CURRENCY_VALUE
    FROM 
        FUND_REPORTED_INFO F
        JOIN FUND_REPORTED_HOLDING H 
            ON F.ACCESSION_NUMBER = H.ACCESSION_NUMBER
    WHERE 
        H.CURRENCY_CODE != H.INVESTMENT_COUNTRY
        AND H.CURRENCY_CODE IS NOT NULL
        AND H.INVESTMENT_COUNTRY IS NOT NULL
)
SELECT 
    SERIES_NAME,
    ISSUER_NAME,
    CURRENCY_CODE as Holding_Currency,
    INVESTMENT_COUNTRY,
    CURRENCY_VALUE
FROM 
    CurrencyMismatches
ORDER BY 
    CAST(CURRENCY_VALUE AS FLOAT) DESC;

-- Portfolio Risk & Derivatives Exposure --
6. "Hey, let's identify any funds with heavy derivatives exposure - over 20% of net assets might be risky."
WITH DerivativeExposure AS (
    SELECT 
        F.SERIES_NAME,
        F.NET_ASSETS,
        SUM(CAST(H.CURRENCY_VALUE AS FLOAT)) as Derivative_Value
    FROM 
        FUND_REPORTED_INFO F
        JOIN FUND_REPORTED_HOLDING H ON F.ACCESSION_NUMBER = H.ACCESSION_NUMBER
        JOIN OTHER_DERIV OD ON H.HOLDING_ID = OD.HOLDING_ID
    GROUP BY 
        F.SERIES_NAME,
        F.NET_ASSETS
)
SELECT 
    SERIES_NAME,
    (Derivative_Value / CAST(NET_ASSETS AS FLOAT) * 100) as Derivative_Percentage
FROM 
    DerivativeExposure
WHERE 
    (Derivative_Value / CAST(NET_ASSETS AS FLOAT)) > 0.20
ORDER BY 
    Derivative_Percentage DESC;

-- Borrower Analysis --
7. "Which borrowers significantly increased their borrowing last quarter? Might signal some risk."
WITH BorrowingTrends AS (
    SELECT 
        B2.NAME as Borrower_Name,
        B2.AGGREGATE_VALUE as Current_Value,
        B1.AGGREGATE_VALUE as Previous_Value,
        ((CAST(B2.AGGREGATE_VALUE AS FLOAT) - CAST(B1.AGGREGATE_VALUE AS FLOAT)) / 
         NULLIF(CAST(B1.AGGREGATE_VALUE AS FLOAT), 0)) * 100 as Increase_Percentage
    FROM 
        BORROWER B1
        JOIN BORROWER B2 
            ON B1.BORROWER_ID = B2.BORROWER_ID
            AND B1.QUARTER < B2.QUARTER
    WHERE 
        B1.AGGREGATE_VALUE IS NOT NULL 
        AND B2.AGGREGATE_VALUE IS NOT NULL
)
SELECT 
    Borrower_Name,
    Current_Value,
    Previous_Value,
    Increase_Percentage
FROM 
    BorrowingTrends
WHERE 
    Increase_Percentage > 25
ORDER BY 
    Increase_Percentage DESC;

-- Performance Analysis --
8. "Find any funds showing losses in their realized gains - might need a closer look at their trading."
SELECT 
    F.SERIES_NAME,
    F.NET_REALIZE_GAIN_NONDERIV_MON1,
    F.NET_REALIZE_GAIN_NONDERIV_MON2,
    F.NET_REALIZE_GAIN_NONDERIV_MON3,
    F.TOTAL_ASSETS
FROM 
    FUND_REPORTED_INFO F
WHERE 
    CAST(NET_REALIZE_GAIN_NONDERIV_MON1 AS FLOAT) < 0
    OR CAST(NET_REALIZE_GAIN_NONDERIV_MON2 AS FLOAT) < 0
    OR CAST(NET_REALIZE_GAIN_NONDERIV_MON3 AS FLOAT) < 0
ORDER BY 
    CAST(NET_REALIZE_GAIN_NONDERIV_MON1 AS FLOAT);

-- Futures Contract Analysis --
9. "Which funds have the biggest unrealized gains in their futures positions? Might want to lock those in."
SELECT 
    F.SERIES_NAME,
    FFC.UNREALIZED_APPRECIATION,
    FFC.NOTIONAL_AMOUNT,
    (CAST(FFC.UNREALIZED_APPRECIATION AS FLOAT) / 
     NULLIF(CAST(FFC.NOTIONAL_AMOUNT AS FLOAT), 0)) * 100 as Return_Percentage
FROM 
    FUT_FWD_NONFOREIGNCUR_CONTRACT FFC
    JOIN FUND_REPORTED_HOLDING H ON FFC.HOLDING_ID = H.HOLDING_ID
    JOIN FUND_REPORTED_INFO F ON H.ACCESSION_NUMBER = F.ACCESSION_NUMBER
WHERE 
    FFC.UNREALIZED_APPRECIATION IS NOT NULL
ORDER BY 
    CAST(FFC.UNREALIZED_APPRECIATION AS FLOAT) DESC
LIMIT 10;

-- Commitment Risk --
10. "Check for funds with large outstanding commitments - both delayed delivery and standby."
WITH CommitmentExposure AS (
    SELECT 
        SERIES_NAME,
        DELAYED_DELIVERY,
        STANDBY_COMMITMENT,
        TOTAL_ASSETS,
        (CAST(DELAYED_DELIVERY AS FLOAT) + CAST(STANDBY_COMMITMENT AS FLOAT)) / 
        NULLIF(CAST(TOTAL_ASSETS AS FLOAT), 0) * 100 as Total_Commitment_Percentage
    FROM 
        FUND_REPORTED_INFO
    WHERE 
        DELAYED_DELIVERY IS NOT NULL 
        AND STANDBY_COMMITMENT IS NOT NULL
)
SELECT 
    SERIES_NAME,
    DELAYED_DELIVERY,
    STANDBY_COMMITMENT,
    Total_Commitment_Percentage
FROM 
    CommitmentExposure
WHERE 
    Total_Commitment_Percentage > 5
ORDER BY 
    Total_Commitment_Percentage DESC;

-- Fair Value Analysis --
11. "Give me a breakdown of holdings by fair value level and issuer type - looking for valuation risk."
SELECT 
    ISSUER_TYPE,
    FAIR_VALUE_LEVEL,
    COUNT(*) as Holding_Count,
    SUM(CAST(CURRENCY_VALUE AS FLOAT)) as Total_Value,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY ISSUER_TYPE) as Percentage_of_Type
FROM 
    FUND_REPORTED_HOLDING
WHERE 
    ISSUER_TYPE IS NOT NULL 
    AND FAIR_VALUE_LEVEL IS NOT NULL
GROUP BY 
    ISSUER_TYPE,
    FAIR_VALUE_LEVEL
ORDER BY 
    ISSUER_TYPE,
    FAIR_VALUE_LEVEL;

-- Collateral Analysis --
12. "Let's see which funds are heavy on non-cash collateral - might affect their liquidity position."
SELECT 
    F.SERIES_NAME,
    F.TOTAL_ASSETS,
    COUNT(SL.HOLDING_ID) as Collateral_Positions,
    SUM(CAST(H.CURRENCY_VALUE AS FLOAT)) as Total_Collateral_Value
FROM 
    FUND_REPORTED_INFO F
    JOIN FUND_REPORTED_HOLDING H ON F.ACCESSION_NUMBER = H.ACCESSION_NUMBER
    JOIN SECURITIES_LENDING SL ON H.HOLDING_ID = SL.HOLDING_ID
WHERE 
    SL.IS_NON_CASH_COLLATERAL = 'Y'
GROUP BY 
    F.SERIES_NAME,
    F.TOTAL_ASSETS
ORDER BY 
    Total_Collateral_Value DESC;

-- Geographic Exposure --
13. "What's our exposure by state? Need to check geographic concentration."
SELECT 
    R.STATE,
    COUNT(DISTINCT R.REGISTRANT_NAME) as Company_Count,
    COUNT(DISTINCT F.SERIES_NAME) as Fund_Count,
    SUM(CAST(F.NET_ASSETS AS FLOAT)) as Total_Net_Assets
FROM 
    REGISTRANT R
    JOIN FUND_REPORTED_INFO F ON R.ACCESSION_NUMBER = F.ACCESSION_NUMBER
WHERE 
    R.STATE IS NOT NULL
GROUP BY 
    R.STATE
ORDER BY 
    Total_Net_Assets DESC;

-- Securities Lending Activity --
14. "Which securities are most actively lent out? Might signal some interesting market dynamics."
SELECT 
    H.ISSUER_NAME,
    COUNT(*) as Lending_Instances,
    SUM(CAST(H.CURRENCY_VALUE AS FLOAT)) as Total_Value_Lent
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
    Lending_Instances DESC,
    Total_Value_Lent DESC;

-- Currency Risk --
15. "Show me funds with big unrealized gains in their foreign currency forwards - might need hedging reviews."
SELECT 
    F.SERIES_NAME,
    COUNT(*) as Forward_Contracts,
    SUM(CAST(FFC.UNREALIZED_APPRECIATION AS FLOAT)) as Total_Unrealized_Gains,
    AVG(CAST(FFC.UNREALIZED_APPRECIATION AS FLOAT)) as Avg_Unrealized_Gain
FROM 
    FUND_REPORTED_INFO F
    JOIN FUND_REPORTED_HOLDING H ON F.ACCESSION_NUMBER = H.ACCESSION_NUMBER
    JOIN FWD_FOREIGNCUR_CONTRACT_SWAP FFC ON H.HOLDING_ID = FFC.HOLDING_ID
GROUP BY 
    F.SERIES_NAME
HAVING 
    SUM(CAST(FFC.UNREALIZED_APPRECIATION AS FLOAT)) > 500000
ORDER BY 
    Total_Unrealized_Gains DESC;

-- Asset Growth Analysis --
16. "How have our fund sizes changed over the past two quarters? Looking for notable shifts."
WITH AssetChanges AS (
    SELECT 
        F1.SERIES_NAME,
        F2.TOTAL_ASSETS as Current_Assets,
        F1.TOTAL_ASSETS as Previous_Assets,
        ((CAST(F2.TOTAL_ASSETS AS FLOAT) - CAST(F1.TOTAL_ASSETS AS FLOAT)) / 
         NULLIF(CAST(F1.TOTAL_ASSETS AS FLOAT), 0)) * 100 as Growth_Rate
    FROM 
        FUND_REPORTED_INFO F1
        JOIN FUND_REPORTED_INFO F2 
            ON F1.SERIES_ID = F2.SERIES_ID
            AND F1.QUARTER < F2.QUARTER
)
SELECT 
    SERIES_NAME,
    Current_Assets,
    Previous_Assets,
    Growth_Rate
FROM 
    AssetChanges
WHERE 
    ABS(Growth_Rate) > 10
ORDER BY 
    Growth_Rate DESC;

-- Regulatory Compliance --
17. "Which companies might need attention - haven't filed reports recently?"
WITH LatestFilings AS (
    SELECT 
        R.REGISTRANT_NAME,
        MAX(S.FILING_DATE) as Last_Filing_Date,
        COUNT(DISTINCT S.QUARTER) as Filing_Count
    FROM 
        REGISTRANT R
        JOIN SUBMISSION S 
            ON R.ACCESSION_NUMBER = S.ACCESSION_NUMBER
    GROUP BY 
        R.REGISTRANT_NAME
)
SELECT 
    REGISTRANT_NAME,
    Last_Filing_Date,
    Filing_Count,
    JULIANDAY('now') - JULIANDAY(Last_Filing_Date) as Days_Since_Last_Filing
FROM 
    LatestFilings
WHERE 
    JULIANDAY('now') - JULIANDAY(Last_Filing_Date) > 100
ORDER BY 
    Days_Since_Last_Filing DESC;

-- Flow Analysis --
18. "Find any funds where assets dropped despite positive sales - might indicate performance issues."
WITH FundFlows AS (
    SELECT 
        F.SERIES_NAME,
        F.NET_ASSETS,
        LAG(F.NET_ASSETS) OVER (PARTITION BY F.SERIES_ID ORDER BY F.QUARTER) as Prev_Assets,
        (F.SALES_FLOW_MON1 + F.SALES_FLOW_MON2 + F.SALES_FLOW_MON3) as Total_Sales
    FROM 
        FUND_REPORTED_INFO F
)
SELECT 
    SERIES_NAME,
    NET_ASSETS,
    Prev_Assets,
    Total_Sales,
    ((CAST(NET_ASSETS AS FLOAT) - CAST(Prev_Assets AS FLOAT)) / 
     NULLIF(CAST(Prev_Assets AS FLOAT), 0)) * 100 as Asset_Change_Pct
FROM 
    FundFlows
WHERE 
    CAST(NET_ASSETS AS FLOAT) < CAST(Prev_Assets AS FLOAT)
    AND CAST(Total_Sales AS FLOAT) > 0
ORDER BY 
    Asset_Change_Pct;

-- Derivative Valuation --
19. "Check for any big gaps between notional amounts and actual values in our derivatives."
WITH NotionalValueGaps AS (
    SELECT 
        F.SERIES_NAME,
        DRIC.NAME as Component_Name,
        CAST(DRIC.NOTIONAL_AMOUNT AS FLOAT) as Notional_Amount,
        CAST(DRIC.VALUE AS FLOAT) as Market_Value,
        ABS(CAST(DRIC.NOTIONAL_AMOUNT AS FLOAT) - CAST(DRIC.VALUE AS FLOAT)) as Value_Gap
    FROM 
        FUND_REPORTED_INFO F
        JOIN FUND_REPORTED_HOLDING H ON F.ACCESSION_NUMBER = H.ACCESSION_NUMBER
        JOIN DESC_REF_INDEX_COMPONENT DRIC ON H.HOLDING_ID = DRIC.HOLDING_ID
    WHERE 
        DRIC.NOTIONAL_AMOUNT IS NOT NULL 
        AND DRIC.VALUE IS NOT NULL
)
SELECT 
    SERIES_NAME,
    Component_Name,
    Notional_Amount,
    Market_Value,
    Value_Gap,
    (Value_Gap / NULLIF(Notional_Amount, 0)) * 100 as Gap_Percentage
FROM 
    NotionalValueGaps
WHERE 
    Value_Gap > 100000
ORDER BY 
    Gap_Percentage DESC;

-- Credit Risk Assessment --
20. "What's the average yield on our defaulted bonds? Need to assess recovery potential."
WITH DefaultedSecurities AS (
    SELECT 
        F.SERIES_NAME,
        DS.ANNUALIZED_RATE,
        H.CURRENCY_VALUE,
        H.ISSUER_NAME
    FROM 
        DEBT_SECURITY DS
        JOIN FUND_REPORTED_HOLDING H ON DS.HOLDING_ID = H.HOLDING_ID
        JOIN FUND_REPORTED_INFO F ON H.ACCESSION_NUMBER = F.ACCESSION_NUMBER
    WHERE 
        DS.IS_DEFAULT = 'Y'
)
SELECT 
    SERIES_NAME,
    ISSUER_NAME,
    ANNUALIZED_RATE,
    CURRENCY_VALUE
FROM 
    DefaultedSecurities
ORDER BY 
    CAST(ANNUALIZED_RATE AS FLOAT) DESC;

-- Credit Spread Risk --
21. "Which funds are most exposed to high-yield credit spreads widening?"
WITH CreditExposure AS (
    SELECT 
        SERIES_NAME,
        CREDIT_SPREAD_10YR_NONINVEST,
        TOTAL_ASSETS,
        (CAST(CREDIT_SPREAD_10YR_NONINVEST AS FLOAT) / 
         NULLIF(CAST(TOTAL_ASSETS AS FLOAT), 0)) * 100 as HY_Exposure_Pct
    FROM 
        FUND_REPORTED_INFO
    WHERE 
        CREDIT_SPREAD_10YR_NONINVEST IS NOT NULL
)
SELECT 
    SERIES_NAME,
    HY_Exposure_Pct,
    TOTAL_ASSETS
FROM 
    CreditExposure
WHERE 
    HY_Exposure_Pct > 10
ORDER BY 
    HY_Exposure_Pct DESC;

-- Counterparty Risk --
22. "Give me our largest derivative counterparty exposures - need to check concentration risk."
WITH CounterpartyExposure AS (
    SELECT 
        DC.DERIVATIVE_COUNTERPARTY_NAME,
        COUNT(DISTINCT F.SERIES_NAME) as Fund_Count,
        SUM(CAST(NFES.NOTIONAL_AMOUNT AS FLOAT)) as Total_Exposure
    FROM 
        DERIVATIVE_COUNTERPARTY DC
        JOIN NONFOREIGN_EXCHANGE_SWAP NFES ON DC.HOLDING_ID = NFES.HOLDING_ID
        JOIN FUND_REPORTED_HOLDING H ON DC.HOLDING_ID = H.HOLDING_ID
        JOIN FUND_REPORTED_INFO F ON H.ACCESSION_NUMBER = F.ACCESSION_NUMBER
    GROUP BY 
        DC.DERIVATIVE_COUNTERPARTY_NAME
)
SELECT 
    DERIVATIVE_COUNTERPARTY_NAME,
    Fund_Count,
    Total_Exposure,
    Total_Exposure / SUM(Total_Exposure) OVER () * 100 as Exposure_Percentage
FROM 
    CounterpartyExposure
ORDER BY 
    Total_Exposure DESC;

-- Liquidation Analysis --
23. "Find funds with high liquidation preference relative to their size - might affect wind-down scenarios."
SELECT 
    SERIES_NAME,
    TOTAL_ASSETS,
    LIQUIDATION_PREFERENCE,
    (CAST(LIQUIDATION_PREFERENCE AS FLOAT) / 
     NULLIF(CAST(TOTAL_ASSETS AS FLOAT), 0)) * 100 as Preference_Ratio
FROM 
    FUND_REPORTED_INFO
WHERE 
    CAST(LIQUIDATION_PREFERENCE AS FLOAT) > 1000000
ORDER BY 
    Preference_Ratio DESC;

-- Convertible Securities Analysis --
24. "Let's look at convertible securities with high conversion ratios - could be significant upside."
SELECT 
    F.SERIES_NAME,
    H.ISSUER_NAME,
    CSC.CONVERSION_RATIO,
    H.CURRENCY_VALUE
FROM 
    FUND_REPORTED_INFO F
    JOIN FUND_REPORTED_HOLDING H ON F.ACCESSION_NUMBER = H.ACCESSION_NUMBER
    JOIN CONVERTIBLE_SECURITY_CURRENCY CSC ON H.HOLDING_ID = CSC.HOLDING_ID
WHERE 
    CAST(CSC.CONVERSION_RATIO AS FLOAT) > 1
ORDER BY 
    CAST(CSC.CONVERSION_RATIO AS FLOAT) DESC;

-- Flow Analysis --
25. "Show me funds facing redemption pressure - where outflows exceed inflows consistently."
WITH FlowAnalysis AS (
    SELECT 
        SERIES_NAME,
        (CAST(REDEMPTION_FLOW_MON1 AS FLOAT) + 
         CAST(REDEMPTION_FLOW_MON2 AS FLOAT) + 
         CAST(REDEMPTION_FLOW_MON3 AS FLOAT)) as Total_Redemptions,
        (CAST(SALES_FLOW_MON1 AS FLOAT) + 
         CAST(SALES_FLOW_MON2 AS FLOAT) + 
         CAST(SALES_FLOW_MON3 AS FLOAT)) as Total_Sales
    FROM 
        FUND_REPORTED_INFO
)
SELECT 
    SERIES_NAME,
    Total_Redemptions,
    Total_Sales,
    (Total_Redemptions - Total_Sales) as Net_Outflow
FROM 
    FlowAnalysis
WHERE 
    Total_Redemptions > Total_Sales
ORDER BY 
    Net_Outflow DESC;

-- Portfolio Manager Strategic Analysis --
26. "How do PIMCO's bond funds compare to their equity funds in terms of growth?"
WITH PIMCOPerformance AS (
    SELECT 
        F.SERIES_NAME,
        CASE 
            WHEN F.SERIES_NAME LIKE '%BOND%' THEN 'Bond'
            WHEN F.SERIES_NAME LIKE '%EQUITY%' THEN 'Equity'
            ELSE 'Other'
        END as Fund_Type,
        M.MONTHLY_TOTAL_RETURN1,
        F.TOTAL_ASSETS
    FROM 
        FUND_REPORTED_INFO F
        JOIN REGISTRANT R ON F.ACCESSION_NUMBER = R.ACCESSION_NUMBER
        JOIN MONTHLY_TOTAL_RETURN M ON F.ACCESSION_NUMBER = M.ACCESSION_NUMBER
    WHERE 
        R.REGISTRANT_NAME LIKE '%PIMCO%'
)
SELECT 
    Fund_Type,
    COUNT(*) as Fund_Count,
    AVG(CAST(MONTHLY_TOTAL_RETURN1 AS FLOAT)) as Avg_Monthly_Return,
    SUM(CAST(TOTAL_ASSETS AS FLOAT)) as Total_AUM
FROM 
    PIMCOPerformance
WHERE 
    Fund_Type IN ('Bond', 'Equity')
GROUP BY 
    Fund_Type;

27. "Which asset categories are driving our best returns this quarter?"
WITH CategoryPerformance AS (
    SELECT 
        H.ASSET_CAT,
        AVG(CAST(M.MONTHLY_TOTAL_RETURN1 AS FLOAT)) as Avg_Return,
        SUM(CAST(H.CURRENCY_VALUE AS FLOAT)) as Total_Value,
        COUNT(DISTINCT F.SERIES_NAME) as Fund_Count
    FROM 
        FUND_REPORTED_HOLDING H
        JOIN FUND_REPORTED_INFO F ON H.ACCESSION_NUMBER = F.ACCESSION_NUMBER
        JOIN MONTHLY_TOTAL_RETURN M ON F.ACCESSION_NUMBER = M.ACCESSION_NUMBER
    WHERE 
        H.ASSET_CAT IS NOT NULL
    GROUP BY 
        H.ASSET_CAT
)
SELECT 
    ASSET_CAT,
    Avg_Return,
    Total_Value,
    Fund_Count
FROM 
    CategoryPerformance
ORDER BY 
    Avg_Return DESC;

28. "Where are we seeing the biggest month-over-month changes in fund flows?"
WITH FlowTrends AS (
    SELECT 
        F.SERIES_NAME,
        F.SALES_FLOW_MON1,
        F.SALES_FLOW_MON2,
        ((CAST(F.SALES_FLOW_MON1 AS FLOAT) - CAST(F.SALES_FLOW_MON2 AS FLOAT)) / 
         NULLIF(CAST(F.SALES_FLOW_MON2 AS FLOAT), 0)) * 100 as Flow_Change_Pct
    FROM 
        FUND_REPORTED_INFO F
    WHERE 
        F.SALES_FLOW_MON1 IS NOT NULL 
        AND F.SALES_FLOW_MON2 IS NOT NULL
)
SELECT 
    SERIES_NAME,
    SALES_FLOW_MON1 as Current_Flow,
    SALES_FLOW_MON2 as Previous_Flow,
    Flow_Change_Pct
FROM 
    FlowTrends
WHERE 
    ABS(Flow_Change_Pct) > 10
ORDER BY 
    ABS(Flow_Change_Pct) DESC;

29. "What's PIMCO's current duration positioning across their major bond funds?"
WITH PIMCODuration AS (
    SELECT 
        F.SERIES_NAME,
        IR.INTRST_RATE_CHANGE_10YR_DV01,
        IR.INTRST_RATE_CHANGE_30YR_DV01,
        F.TOTAL_ASSETS
    FROM 
        FUND_REPORTED_INFO F
        JOIN REGISTRANT R ON F.ACCESSION_NUMBER = R.ACCESSION_NUMBER
        JOIN INTEREST_RATE_RISK IR ON F.ACCESSION_NUMBER = IR.ACCESSION_NUMBER
    WHERE 
        R.REGISTRANT_NAME LIKE '%PIMCO%'
        AND F.SERIES_NAME LIKE '%BOND%'
)
SELECT 
    SERIES_NAME,
    CAST(INTRST_RATE_CHANGE_10YR_DV01 AS FLOAT) as Ten_Year_Duration,
    CAST(INTRST_RATE_CHANGE_30YR_DV01 AS FLOAT) as Thirty_Year_Duration,
    TOTAL_ASSETS
FROM 
    PIMCODuration
ORDER BY 
    CAST(TOTAL_ASSETS AS FLOAT) DESC;

30. "How are our largest funds positioned in terms of credit quality?"
WITH CreditQuality AS (
    SELECT 
        F.SERIES_NAME,
        F.CREDIT_SPREAD_10YR_INVEST,
        F.CREDIT_SPREAD_10YR_NONINVEST,
        F.TOTAL_ASSETS,
        CAST(F.CREDIT_SPREAD_10YR_INVEST AS FLOAT) / 
        NULLIF(CAST(F.CREDIT_SPREAD_10YR_INVEST AS FLOAT) + 
               CAST(F.CREDIT_SPREAD_10YR_NONINVEST AS FLOAT), 0) * 100 as IG_Percentage
    FROM 
        FUND_REPORTED_INFO F
    WHERE 
        CAST(F.TOTAL_ASSETS AS FLOAT) > 1000000000
)
SELECT 
    SERIES_NAME,
    IG_Percentage,
    TOTAL_ASSETS
FROM 
    CreditQuality
ORDER BY 
    CAST(TOTAL_ASSETS AS FLOAT) DESC;

31. "Which sectors are seeing the biggest shifts in allocation this quarter?"
WITH SectorShifts AS (
    SELECT 
        H.ASSET_CAT,
        S.QUARTER,
        SUM(CAST(H.CURRENCY_VALUE AS FLOAT)) as Total_Value
    FROM 
        FUND_REPORTED_HOLDING H
        JOIN SUBMISSION S ON H.ACCESSION_NUMBER = S.ACCESSION_NUMBER
    GROUP BY 
        H.ASSET_CAT,
        S.QUARTER
)
SELECT 
    s1.ASSET_CAT,
    s1.Total_Value as Current_Value,
    s2.Total_Value as Previous_Value,
    ((s1.Total_Value - s2.Total_Value) / s2.Total_Value * 100) as Change_Percentage
FROM 
    SectorShifts s1
    JOIN SectorShifts s2 
        ON s1.ASSET_CAT = s2.ASSET_CAT
        AND s1.QUARTER > s2.QUARTER
ORDER BY 
    ABS(Change_Percentage) DESC;

32. "Give me a list of funds that seem to be changing their risk profile significantly."
WITH RiskMetrics AS (
    SELECT 
        F.SERIES_NAME,
        F.QUARTER,
        (CAST(F.CREDIT_SPREAD_10YR_NONINVEST AS FLOAT) / 
         NULLIF(CAST(F.TOTAL_ASSETS AS FLOAT), 0)) * 100 as HY_Exposure,
        (CAST(F.BORROWING_PAY_WITHIN_1YR AS FLOAT) / 
         NULLIF(CAST(F.TOTAL_ASSETS AS FLOAT), 0)) * 100 as Leverage_Ratio
    FROM 
        FUND_REPORTED_INFO F
)
SELECT 
    r1.SERIES_NAME,
    r1.HY_Exposure - r2.HY_Exposure as HY_Exposure_Change,
    r1.Leverage_Ratio - r2.Leverage_Ratio as Leverage_Change
FROM 
    RiskMetrics r1
    JOIN RiskMetrics r2 
        ON r1.SERIES_NAME = r2.SERIES_NAME
        AND r1.QUARTER > r2.QUARTER
WHERE 
    ABS(r1.HY_Exposure - r2.HY_Exposure) > 5
    OR ABS(r1.Leverage_Ratio - r2.Leverage_Ratio) > 5
ORDER BY 
    ABS(r1.HY_Exposure - r2.HY_Exposure) + ABS(r1.Leverage_Ratio - r2.Leverage_Ratio) DESC;

33. "What's our current cash position across funds compared to last quarter?"
WITH CashPositions AS (
    SELECT 
        F.SERIES_NAME,
        F.QUARTER,
        CAST(F.CASH_NOT_RPTD_IN_C_OR_D AS FLOAT) / 
        NULLIF(CAST(F.TOTAL_ASSETS AS FLOAT), 0) * 100 as Cash_Percentage
    FROM 
        FUND_REPORTED_INFO F
)
SELECT 
    c1.SERIES_NAME,
    c1.Cash_Percentage as Current_Cash,
    c2.Cash_Percentage as Previous_Cash,
    c1.Cash_Percentage - c2.Cash_Percentage as Cash_Change
FROM 
    CashPositions c1
    JOIN CashPositions c2 
        ON c1.SERIES_NAME = c2.SERIES_NAME
        AND c1.QUARTER > c2.QUARTER
WHERE 
    ABS(c1.Cash_Percentage - c2.Cash_Percentage) > 2
ORDER BY 
    ABS(Cash_Change) DESC;

34. "Show me our best performing strategies in rising rate environments."
WITH RatePerformance AS (
    SELECT 
        F.SERIES_NAME,
        M.MONTHLY_TOTAL_RETURN1,
        IR.INTRST_RATE_CHANGE_10YR_DV01
    FROM 
        FUND_REPORTED_INFO F
        JOIN MONTHLY_TOTAL_RETURN M ON F.ACCESSION_NUMBER = M.ACCESSION_NUMBER
        JOIN INTEREST_RATE_RISK IR ON F.ACCESSION_NUMBER = IR.ACCESSION_NUMBER
    WHERE 
        CAST(IR.INTRST_RATE_CHANGE_10YR_DV01 AS FLOAT) > 0
)
SELECT 
    SERIES_NAME,
    AVG(CAST(MONTHLY_TOTAL_RETURN1 AS FLOAT)) as Avg_Return,
    AVG(CAST(INTRST_RATE_CHANGE_10YR_DV01 AS FLOAT)) as Avg_Rate_Sensitivity
FROM 
    RatePerformance
GROUP BY 
    SERIES_NAME
ORDER BY 
    Avg_Return DESC
LIMIT 10;

35. "What's the geographic distribution of our international holdings?"
SELECT 
    H.INVESTMENT_COUNTRY,
    COUNT(DISTINCT F.SERIES_NAME) as Fund_Count,
    SUM(CAST(H.CURRENCY_VALUE AS FLOAT)) as Total_Value,
    SUM(CAST(H.CURRENCY_VALUE AS FLOAT)) / 
    SUM(SUM(CAST(H.CURRENCY_VALUE AS FLOAT))) OVER () * 100 as Percentage
FROM 
    FUND_REPORTED_HOLDING H
    JOIN FUND_REPORTED_INFO F ON H.ACCESSION_NUMBER = F.ACCESSION_NUMBER
WHERE 
    H.INVESTMENT_COUNTRY IS NOT NULL
    AND H.INVESTMENT_COUNTRY != 'US'
GROUP BY 
    H.INVESTMENT_COUNTRY
ORDER BY 
    Total_Value DESC;

36. "Which of our funds have the most consistent monthly returns?"
WITH ReturnConsistency AS (
    SELECT 
        F.SERIES_NAME,
        STDDEV(CAST(M.MONTHLY_TOTAL_RETURN1 AS FLOAT)) as Return_StdDev,
        AVG(CAST(M.MONTHLY_TOTAL_RETURN1 AS FLOAT)) as Avg_Return
    FROM 
        FUND_REPORTED_INFO F
        JOIN MONTHLY_TOTAL_RETURN M ON F.ACCESSION_NUMBER = M.ACCESSION_NUMBER
    GROUP BY 
        F.SERIES_NAME
    HAVING 
        COUNT(*) >= 3
)
SELECT 
    SERIES_NAME,
    Avg_Return,
    Return_StdDev,
    CASE 
        WHEN Return_StdDev = 0 THEN NULL 
        ELSE Avg_Return / Return_StdDev 
    END as Sharpe_Ratio
FROM 
    ReturnConsistency
WHERE 
    Return_StdDev > 0
ORDER BY 
    Return_StdDev ASC
LIMIT 15;

37. "Let's see which funds are most active in derivatives across different instrument types."
WITH DerivativeUsage AS (
    SELECT 
        F.SERIES_NAME,
        COUNT(DISTINCT CASE WHEN OD.HOLDING_ID IS NOT NULL THEN 'Other' END) +
        COUNT(DISTINCT CASE WHEN FFC.HOLDING_ID IS NOT NULL THEN 'FX' END) +
        COUNT(DISTINCT CASE WHEN NES.HOLDING_ID IS NOT NULL THEN 'Swap' END) as Derivative_Types,
        COUNT(*) as Total_Positions
    FROM 
        FUND_REPORTED_INFO F
        LEFT JOIN OTHER_DERIV OD ON F.ACCESSION_NUMBER = OD.HOLDING_ID
        LEFT JOIN FWD_FOREIGNCUR_CONTRACT_SWAP FFC ON F.ACCESSION_NUMBER = FFC.HOLDING_ID
        LEFT JOIN NONFOREIGN_EXCHANGE_SWAP NES ON F.ACCESSION_NUMBER = NES.HOLDING_ID
    GROUP BY 
        F.SERIES_NAME
)
SELECT 
    SERIES_NAME,
    Derivative_Types,
    Total_Positions
FROM 
    DerivativeUsage
WHERE 
    Derivative_Types > 0
ORDER BY 
    Derivative_Types DESC, Total_Positions DESC;

38. "What's our current exposure to emerging market debt?"
WITH EMDebt AS (
    SELECT 
        F.SERIES_NAME,
        SUM(CAST(H.CURRENCY_VALUE AS FLOAT)) as EM_Debt_Value,
        CAST(F.TOTAL_ASSETS AS FLOAT) as Total_Assets
    FROM 
        FUND_REPORTED_INFO F
        JOIN FUND_REPORTED_HOLDING H ON F.ACCESSION_NUMBER = H.ACCESSION_NUMBER
    WHERE 
        H.ASSET_CAT LIKE '%DEBT%'
        AND H.INVESTMENT_COUNTRY NOT IN ('US', 'GB', 'DE', 'FR', 'JP', 'CA', 'IT')
    GROUP BY 
        F.SERIES_NAME,
        F.TOTAL_ASSETS
)
SELECT 
    SERIES_NAME,
    EM_Debt_Value,
    (EM_Debt_Value / Total_Assets * 100) as EM_Debt_Percentage
FROM 
    EMDebt
WHERE 
    EM_Debt_Value > 0
ORDER BY 
    EM_Debt_Percentage DESC;

39. "How diverse are our income sources across the portfolio?"
WITH IncomeAnalysis AS (
    SELECT 
        F.SERIES_NAME,
        SUM(CASE 
            WHEN DS.COUPON_TYPE = 'Fixed' THEN CAST(H.CURRENCY_VALUE AS FLOAT) 
            ELSE 0 
        END) as Fixed_Income,
        SUM(CASE 
            WHEN DS.COUPON_TYPE = 'Floating' THEN CAST(H.CURRENCY_VALUE AS FLOAT) 
            ELSE 0 
        END) as Floating_Income,
        SUM(CASE 
            WHEN SL.IS_LOAN_BY_FUND = 'Y' THEN CAST(H.CURRENCY_VALUE AS FLOAT) 
            ELSE 0 
        END) as Securities_Lending_Income,
        CAST(F.TOTAL_ASSETS AS FLOAT) as Total_Assets
    FROM 
        FUND_REPORTED_INFO F
        JOIN FUND_REPORTED_HOLDING H 
            ON F.ACCESSION_NUMBER = H.ACCESSION_NUMBER
        LEFT JOIN DEBT_SECURITY DS 
            ON H.HOLDING_ID = DS.HOLDING_ID
        LEFT JOIN SECURITIES_LENDING SL 
            ON H.HOLDING_ID = SL.HOLDING_ID
    GROUP BY 
        F.SERIES_NAME,
        F.TOTAL_ASSETS
)
SELECT 
    SERIES_NAME,
    (Fixed_Income / Total_Assets * 100) as Fixed_Income_Pct,
    (Floating_Income / Total_Assets * 100) as Floating_Income_Pct,
    (Securities_Lending_Income / Total_Assets * 100) as Sec_Lending_Pct,
    ((Fixed_Income + Floating_Income + Securities_Lending_Income) / Total_Assets * 100) as Total_Income_Pct,
    Total_Assets
FROM 
    IncomeAnalysis
WHERE 
    Total_Assets > 0
ORDER BY 
    Total_Income_Pct DESC;

40. "Give me a complete risk profile of PIMCO's largest funds - looking at duration, credit, and leverage exposure"
WITH PIMCORiskProfile AS (
    SELECT 
        F.SERIES_NAME,
        F.TOTAL_ASSETS,
        -- Duration Risk
        IR.INTRST_RATE_CHANGE_10YR_DV01 as Duration_Risk,
        -- Credit Risk
        (CAST(F.CREDIT_SPREAD_10YR_NONINVEST AS FLOAT) / 
         NULLIF(CAST(F.TOTAL_ASSETS AS FLOAT), 0)) * 100 as High_Yield_Exposure,
        -- Leverage
        (CAST(F.BORROWING_PAY_WITHIN_1YR AS FLOAT) + 
         CAST(F.BORROWING_PAY_AFTER_1YR AS FLOAT)) / 
         NULLIF(CAST(F.TOTAL_ASSETS AS FLOAT), 0) * 100 as Leverage_Ratio,
        -- Derivatives Exposure
        COUNT(DISTINCT OD.HOLDING_ID) as Derivative_Positions,
        -- Liquidity Profile
        CAST(F.CASH_NOT_RPTD_IN_C_OR_D AS FLOAT) / 
        NULLIF(CAST(F.TOTAL_ASSETS AS FLOAT), 0) * 100 as Cash_Position,
        -- Recent Performance
        M.MONTHLY_TOTAL_RETURN1
    FROM 
        FUND_REPORTED_INFO F
        JOIN REGISTRANT R 
            ON F.ACCESSION_NUMBER = R.ACCESSION_NUMBER
        LEFT JOIN INTEREST_RATE_RISK IR 
            ON F.ACCESSION_NUMBER = IR.ACCESSION_NUMBER
        LEFT JOIN OTHER_DERIV OD 
            ON F.ACCESSION_NUMBER = OD.HOLDING_ID
        LEFT JOIN MONTHLY_TOTAL_RETURN M 
            ON F.ACCESSION_NUMBER = M.ACCESSION_NUMBER
    WHERE 
        R.REGISTRANT_NAME LIKE '%PIMCO%'
        AND F.TOTAL_ASSETS IS NOT NULL
    GROUP BY 
        F.SERIES_NAME,
        F.TOTAL_ASSETS,
        IR.INTRST_RATE_CHANGE_10YR_DV01,
        F.CREDIT_SPREAD_10YR_NONINVEST,
        F.BORROWING_PAY_WITHIN_1YR,
        F.BORROWING_PAY_AFTER_1YR,
        F.CASH_NOT_RPTD_IN_C_OR_D,
        M.MONTHLY_TOTAL_RETURN1
)
SELECT 
    SERIES_NAME,
    CAST(TOTAL_ASSETS AS FLOAT) / 1000000 as Assets_MM,
    Duration_Risk as Duration_DV01,
    High_Yield_Exposure as HY_Pct,
    Leverage_Ratio as Leverage_Pct,
    Derivative_Positions,
    Cash_Position as Cash_Pct,
    CAST(MONTHLY_TOTAL_RETURN1 AS FLOAT) as Latest_Monthly_Return,
    CASE
        WHEN Duration_Risk > 1 AND High_Yield_Exposure > 20 THEN 'High Risk'
        WHEN Duration_Risk > 1 OR High_Yield_Exposure > 20 THEN 'Moderate Risk'
        ELSE 'Conservative'
    END as Risk_Category
FROM 
    PIMCORiskProfile
ORDER BY 
    CAST(TOTAL_ASSETS AS FLOAT) DESC
LIMIT 15;

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
    reasoning_instruction +
    gpt_queries_easy +
    gpt_queries_medium +
    gpt_queries_hard +
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