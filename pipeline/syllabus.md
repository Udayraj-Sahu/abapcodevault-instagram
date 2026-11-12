3. ABAP Data Dictionary (DDIC)
1. DDIC basics [B]
    ◦ Role of DDIC, SE11, activation, runtime objects (nametab)
2. Domains & data elements [B]
    ◦ Domain: data type, length, value range, fixed values, value table, conversion routine
    ◦ Data element: field labels, documentation, search help & parameter ID assignment
3. Tables [B]
    ◦ Transparent, pooled, cluster tables (and their S/4HANA status)
    ◦ Delivery class (A, C, L, G, E, S, W), data class, size category
    ◦ Technical settings, buffering (single, generic, full), logging
    ◦ Primary key, foreign keys, check tables, cardinality
    ◦ Include structures and append structures; currency/quantity reference fields
4. Structures & table types [B]
    ◦ Flat, nested and deep structures; table type with key definition
5. Views [I]
    ◦ Database, projection, maintenance, help views
    ◦ Maintenance view + table maintenance generator (SE54, SM30, SM34 view clusters)
6. Search helps [I]
    ◦ Elementary vs collective, selection method, dialog types, search help exits
7. Lock objects [I]
    ◦ Lock modes (E, S, X, O), generated ENQUEUE_/DEQUEUE_ function modules, SM12
8. Indexes [I]
    ◦ Primary vs secondary indexes, when to create, unique index
9. Type groups & enhancement categories [A]
    ◦ Type pools, enhancement category for append/include extensibility
10. Database utility [A]
    ◦ SE14 adjust/convert, table conversion after structural change
4. Internal Tables
1. Concepts [B]
    ◦ Work area vs header line (obsolete), line type, table key, table kind
2. Table kinds [B]
    ◦ Standard, sorted, hashed; when to use each; access cost (linear, binary, hash)
    ◦ Unique vs non-unique keys; default key pitfalls
3. Filling tables [B]
    ◦ APPEND, INSERT, COLLECT, APPEND LINES OF, SELECT ... INTO TABLE
4. Reading & looping [B]
    ◦ READ TABLE ... WITH KEY / INDEX / BINARY SEARCH, TRANSPORTING NO FIELDS
    ◦ LOOP AT ... WHERE, ASSIGNING <fs>, REFERENCE INTO
5. Changing & deleting [B]
    ◦ MODIFY, MODIFY ... TRANSPORTING, DELETE ... WHERE, DELETE ADJACENT DUPLICATES
    ◦ SORT, CLEAR, REFRESH, FREE (memory differences)
6. Control-level processing [I]
    ◦ AT FIRST / AT NEW / AT END OF / AT LAST, SUM, sort-order prerequisites
7. Secondary keys [A]
    ◦ Sorted/hashed secondary keys, USING KEY, key lazy update
8. Nested & deep tables [I]
    ◦ Tables inside structures, parallel cursor technique for nested loops
9. Modern table expressions [I]
    ◦ itab[ key = val ], line_exists( ), line_index( ), lines( )
    ◦ VALUE #( ), FOR ... IN, REDUCE, FILTER, CORRESPONDING #( ), LOOP AT ... GROUP BY
10. Ranges [B]
    ◦ RANGES / TYPE RANGE OF, SIGN / OPTION / LOW / HIGH, use in WHERE
5. Open SQL / ABAP SQL
1. SELECT basics [B]
    ◦ SELECT SINGLE, SELECT ... UP TO n ROWS, SELECT ... ENDSELECT (and why to avoid it)
    ◦ INTO TABLE, INTO CORRESPONDING FIELDS OF, APPENDING TABLE
2. WHERE conditions [B]
    ◦ =, IN (ranges/select-options), LIKE, BETWEEN, IS NULL, ORDER BY, DISTINCT
3. Joins & subqueries [I]
    ◦ INNER JOIN, LEFT OUTER JOIN, joining on multiple keys, subqueries with EXISTS / IN
4. FOR ALL ENTRIES [I]
    ◦ Empty driver table check, duplicate removal, key completeness
5. Aggregates [I]
    ◦ COUNT, SUM, AVG, MIN, MAX, GROUP BY, HAVING
6. DML statements [B]
    ◦ INSERT, UPDATE, MODIFY, DELETE on DB tables; SY-SUBRC & SY-DBCNT
7. Transactions & LUW [I]
    ◦ COMMIT WORK, ROLLBACK WORK, DB LUW vs SAP LUW
    ◦ Update function modules (CALL FUNCTION ... IN UPDATE TASK), PERFORM ... ON COMMIT
8. New ABAP SQL syntax (7.40+) [I]
    ◦ Comma-separated fields, @ host variables, inline @DATA( ), CASE, COALESCE, string/arith functions
    ◦ UNION, CTEs (WITH), window functions in newer releases
9. Native & dynamic SQL [A]
    ◦ Dynamic WHERE / field lists, EXEC SQL, ADBC (cl_sql_statement)
10. Database cursor [A]
    ◦ OPEN CURSOR, FETCH NEXT CURSOR ... PACKAGE SIZE, CLOSE CURSOR
6. Modularization Techniques
1. Includes [B]
    ◦ Top include, selection-screen include, forms include; include vs program
2. Macros [B]
    ◦ DEFINE ... END-OF-DEFINITION, limitations, why to avoid in new code
3. Subroutines [B]
    ◦ FORM / PERFORM, USING, CHANGING, TABLES; pass by value vs reference
    ◦ External perform, obsolete status in modern ABAP
4. Function modules [B]
    ◦ Function groups (SE80/SE37), global data in function groups
    ◦ Import, export, changing, tables, exceptions; RAISE / MESSAGE ... RAISING
    ◦ Normal vs remote-enabled vs update function modules
    ◦ Calling: CALL FUNCTION, EXCEPTIONS, STARTING NEW TASK (asynchronous), IN BACKGROUND TASK
5. Methods [I]
    ◦ Local vs global class methods (see OOP section) as the modern default
6. Program calls [I]
    ◦ SUBMIT ... AND RETURN / VIA SELECTION-SCREEN / WITH, CALL TRANSACTION, LEAVE TO TRANSACTION
7. Reports
1. Selection screens [B]
    ◦ PARAMETERS, SELECT-OPTIONS, SELECTION-SCREEN BEGIN OF BLOCK / LINE, radio buttons, checkboxes, list boxes
    ◦ OBLIGATORY, DEFAULT, NO INTERVALS, NO-EXTENSION, MODIF ID, MATCHCODE OBJECT
    ◦ Variants, text elements (selection texts, text symbols), F4 help for custom fields
2. Report events [B]
    ◦ LOAD-OF-PROGRAM, INITIALIZATION, AT SELECTION-SCREEN OUTPUT, AT SELECTION-SCREEN ON <field> / ON VALUE-REQUEST / ON HELP-REQUEST
    ◦ START-OF-SELECTION, END-OF-SELECTION, TOP-OF-PAGE, END-OF-PAGE
3. Classical reports [B]
    ◦ WRITE, ULINE, SKIP, NEW-PAGE, FORMAT COLOR / INTENSIFIED / HOTSPOT, LINE-SIZE, LINE-COUNT
4. Interactive reports [I]
    ◦ AT LINE-SELECTION, AT USER-COMMAND, AT PFnn, HIDE, GET CURSOR, READ LINE, SY-LSIND (up to 20 secondary lists)
    ◦ TOP-OF-PAGE DURING LINE-SELECTION, GUI status for lists (SE41)
5. ALV — function module based [B]
    ◦ REUSE_ALV_GRID_DISPLAY, REUSE_ALV_LIST_DISPLAY, field catalog, layout, sort, events, top-of-page
    ◦ Hierarchical & blocked ALV
6. ALV — OO [I]
    ◦ CL_GUI_ALV_GRID with custom container: field catalog, toolbar, HANDLE_USER_COMMAND, DOUBLE_CLICK, HOTSPOT_CLICK, editable ALV, DATA_CHANGED
    ◦ CL_SALV_TABLE (SALV): functions, columns, sorts, aggregations, events, popups
    ◦ CL_SALV_TREE, CL_SALV_HIERSEQ_TABLE
7. Background processing [I]
    ◦ SM36/SM37, JOB_OPEN / JOB_SUBMIT / JOB_CLOSE, SY-BATCH, spool output (SP01)
8. Logical databases (legacy) [A]
    ◦ LDB concept, GET events, NODES — read only for legacy support (e.g. HR PNP/PNPCE)
8. Dialog / Module Pool Programming
1. Basics [I]
    ◦ Module pool program (type M), transaction code (SE93), screen numbers, screen flow
2. Screen Painter (SE51) [I]
    ◦ Layout editor, element list, attributes, flow logic
    ◦ Screen elements: input/output fields, text fields, push buttons, radio buttons, checkboxes, frames, subscreen areas, custom controls
3. Flow logic events [I]
    ◦ PROCESS BEFORE OUTPUT (PBO), PROCESS AFTER INPUT (PAI), PROCESS ON VALUE-REQUEST (POV), PROCESS ON HELP-REQUEST (POH)
    ◦ MODULE, FIELD ... MODULE, CHAIN ... ENDCHAIN, ON INPUT / ON REQUEST, AT EXIT-COMMAND
4. GUI status & title (SE41) [I]
    ◦ Function codes, SET PF-STATUS, SET TITLEBAR, OK_CODE handling, function types (E for exit)
5. Screen navigation [I]
    ◦ CALL SCREEN, SET SCREEN, LEAVE SCREEN, LEAVE TO SCREEN, modal dialog boxes (STARTING AT)
6. Dynamic screen modification [I]
    ◦ LOOP AT SCREEN, SCREEN-INPUT / ACTIVE / INVISIBLE / REQUIRED, MODIFY SCREEN, screen groups
7. Table control & step loops [I]
    ◦ CONTROLS ... TYPE TABLEVIEW, LOOP AT itab WITH CONTROL, scrolling, line selection, insert/delete rows
8. Tabstrip control [I]
    ◦ Tabstrips with subscreens, scrolling at application server vs SAPGUI
9. Subscreens [I]
    ◦ CALL SUBSCREEN, INCLUDING, subscreen data transfer
10. Controls framework [A]
    ◦ Custom container, docking/splitter containers, text editor, picture control, tree control, HTML viewer
11. Validations & locking [I]
    ◦ Field validations, error messages in PAI, lock objects in dialog transactions
9. Object-Oriented ABAP
1. OOP concepts [I]
    ◦ Class, object, encapsulation, inheritance, polymorphism, abstraction
2. Local & global classes [I]
    ◦ CLASS ... DEFINITION / IMPLEMENTATION, SE24 class builder, DEFERRED, LOAD
    ◦ Visibility sections: PUBLIC, PROTECTED, PRIVATE; friends
3. Attributes & methods [I]
    ◦ Instance vs static (CLASS-DATA, CLASS-METHODS), constants, read-only attributes
    ◦ Parameters: importing, exporting, changing, returning; OPTIONAL, DEFAULT, functional methods
4. Constructors [I]
    ◦ Instance CONSTRUCTOR, CLASS_CONSTRUCTOR, order of execution, NEW #( ) vs CREATE OBJECT
5. Inheritance [I]
    ◦ INHERITING FROM, REDEFINITION, super->, FINAL, ABSTRACT classes/methods
6. Interfaces [I]
    ◦ INTERFACES, alias names, interface methods, compound interfaces
7. Polymorphism & casting [I]
    ◦ Up-cast (narrowing) and down-cast (widening) with ?= / CAST #( ), IS INSTANCE OF, CASE TYPE OF
8. Events [I]
    ◦ EVENTS, RAISE EVENT, SET HANDLER, instance vs static events
9. Object instantiation control [A]
    ◦ CREATE PRIVATE / PROTECTED / PUBLIC, singleton pattern, factory methods
10. Design patterns in ABAP [A]
    ◦ Singleton, factory, MVC, observer, strategy, decorator, persistence layer
11. Persistent & transaction services [A]
    ◦ Persistent classes, object services, CL_OS_SYSTEM
12. RTTS (Run Time Type Services) [A]
    ◦ RTTI: CL_ABAP_TYPEDESCR, CL_ABAP_STRUCTDESCR; RTTC: dynamic structure/table creation
13. Clean ABAP & SOLID [A]
    ◦ SAP Clean ABAP style guide, SOLID principles, dependency injection
10. Exceptions, Debugging & Testing
1. Classical exceptions [B]
    ◦ SY-SUBRC checks, function module EXCEPTIONS, CATCH SYSTEM-EXCEPTIONS (obsolete)
2. Class-based exceptions [I]
    ◦ TRY / CATCH / CLEANUP / ENDTRY, RAISE EXCEPTION TYPE, RETRY, RESUME
    ◦ Exception classes: CX_STATIC_CHECK, CX_DYNAMIC_CHECK, CX_NO_CHECK; exception texts via message class/OTR
3. Debugger [B]
    ◦ /h, breakpoints (session, external, BREAK-POINT, BREAK <user>), watchpoints
    ◦ Step F5/F6/F7/F8, changing variable values, table/structure view, call stack
    ◦ Debugging update tasks, background jobs (JDBG / SM50), popups (debug via shortcut file), system debugging
4. Runtime analysis & logs [I]
    ◦ ST22 (short dumps), SM21 (system log), SLG1 / SLG0 (application log via BAL_* FMs)
    ◦ Checkpoint groups (SAAB): ASSERT, LOG-POINT
5. Static checks [I]
    ◦ Extended program check (SLIN), Code Inspector (SCI), ATC
6. Unit testing [A]
    ◦ ABAP Unit: test classes FOR TESTING, RISK LEVEL, DURATION, cl_abap_unit_assert, setup/teardown
    ◦ Test doubles: test seams, cl_abap_testdouble, OSQL test environment, CDS test environment
11. Forms & Output
1. SAPscript [I]
    ◦ SE71 form painter: pages, windows (main, variable, constant), page windows, paragraph & character formats
    ◦ Print program: OPEN_FORM, START_FORM, WRITE_FORM, END_FORM, CLOSE_FORM
    ◦ Standard texts (SO10), INCLUDE, PERFORM in SAPscript, logo upload (SE78)
2. SmartForms [I]
    ◦ SMARTFORMS transaction: global settings, form interface, global definitions, initialization
    ◦ Pages, windows, text nodes, tables, templates, loops, alternatives, commands, program lines
    ◦ Styles (SMARTSTYLES), calling via SSF_FUNCTION_MODULE_NAME, control & output parameters
    ◦ Converting to PDF: CONVERT_OTF, emailing with CL_BCS
3. Adobe Forms (SFP) [I]
    ◦ Interface (ABAP dictionary / XML), context, Adobe LiveCycle Designer layout
    ◦ Print program: FP_JOB_OPEN, FP_FUNCTION_MODULE_NAME, FP_JOB_CLOSE; ADS configuration
    ◦ FormCalc / JavaScript scripting, interactive forms, PDF output & email
4. Output management [I]
    ◦ NACE output types / condition records (ECC), BRF+ output management (S/4HANA)
    ◦ Spool & printer setup (SPAD), SP01/SP02
5. File & email output [I]
    ◦ GUI_DOWNLOAD / GUI_UPLOAD, OPEN DATASET (application server, AL11), Excel export, CL_BCS email with attachments
12. Enhancements & Modifications
1. Enhancement concept [I]
    ◦ Why enhance not modify; modification assistant (SPAU/SPDD) and access keys
2. User exits [I]
    ◦ Form-based exits (e.g. MV45AFZZ in SD), finding them via includes
3. Customer exits [I]
    ◦ SMOD / CMOD projects; function exits (CALL CUSTOMER-FUNCTION), screen exits, menu exits
4. BAdIs [I]
    ◦ Classic BAdI (SE18/SE19, CL_EXITHANDLER), kernel/new BAdI (GET BADI, CALL BADI)
    ◦ Single vs multiple use, filter-dependent BAdIs, fallback class
5. Enhancement Framework [I]
    ◦ Implicit enhancement points (start/end of FM, form, method), explicit enhancement points & sections
    ◦ Enhancement spots and composite enhancement spots
6. Class/FM enhancements [A]
    ◦ Pre-, post- and overwrite methods, additional parameters
7. Business Transaction Events (BTE) [A]
    ◦ FIBF, P&S vs process interfaces (mainly FI)
8. Validations & substitutions [A]
    ◦ GGB0 / GGB1 (FI/CO)
9. Finding enhancements [I]
    ◦ Techniques: CL_EXITHANDLER breakpoint, SE84, package search, ST05 trace, “find BAdI” reports
10. Key S/4HANA extensibility [A]
    ◦ Key user extensibility (custom fields & logic), developer extensibility, side-by-side on BTP
13. Interfaces & Data Migration
1. File handling [B]
    ◦ Presentation server (GUI_UPLOAD, cl_gui_frontend_services), application server (OPEN / READ / TRANSFER / CLOSE DATASET), Excel upload (TEXT_CONVERT_XLS_TO_SAP, ALSM_EXCEL_TO_INTERNAL_TABLE)
2. BDC (Batch Data Communication) [I]
    ◦ Recording (SHDB), BDCDATA structure
    ◦ Call transaction method (modes A/E/N, update S/A/L, MESSAGES INTO), session method (BDC_OPEN_GROUP / INSERT / CLOSE, SM35)
    ◦ Table control handling in BDC, CTU_PARAMS
3. LSMW [I]
    ◦ 14 steps, recording / batch input / BAPI / IDoc methods (legacy in S/4)
4. S/4HANA Migration Cockpit [A]
    ◦ LTMC / Migrate Your Data app, staging tables, migration objects
5. BAPI [I]
    ◦ BOR (SWO1), finding BAPIs (BAPI transaction), BAPIRET2 return handling
    ◦ BAPI_TRANSACTION_COMMIT / ROLLBACK, extension structures (EXTENSIONIN), custom BAPI creation
6. RFC [I]
    ◦ Remote-enabled FMs, RFC destinations (SM59), sRFC, aRFC, tRFC, qRFC, bgRFC
7. ALE & IDocs [A]
    ◦ IDoc structure: control, data, status records; basic types, extensions, message types
    ◦ WE30, WE31, WE81, WE82, WE20 partner profiles, BD64 distribution model, WE02/WE05, BD87
    ◦ Inbound/outbound process codes, custom IDoc FMs, change pointers (BD50, BD52, BD21)
8. Web services & APIs [A]
    ◦ SOAP services (SE80 / SOAMANAGER), REST via CL_HTTP_CLIENT, JSON (/ui2/cl_json, xco_cp_json)
    ◦ OData with SAP Gateway: SEGW, DPC_EXT / MPC_EXT, CRUD-Q methods, $expand, deep insert, /IWFND/MAINT_SERVICE, /IWFND/GW_CLIENT
9. XML & transformations [A]
    ◦ CALL TRANSFORMATION, XSLT & Simple Transformations (STRANS), iXML library
10. Workflow basics [A]
    ◦ SWDD workflow builder, business objects, events, agents, SWI1 / SWEL
14. Performance Tuning
1. Analysis tools [I]
    ◦ ST05 (SQL / buffer / RFC trace), SAT / SE30 (runtime analysis), ST12, SQLM, SWLT, STAD, ST04
2. Database access rules [I]
    ◦ Select only needed fields (no SELECT *), use full/primary keys and indexes, avoid SELECT in LOOP
    ◦ Use joins or FOR ALL ENTRIES correctly, aggregate in DB, use UP TO n ROWS, avoid nested SELECTs
    ◦ Table buffering and BYPASSING BUFFER
3. Internal table rules [I]
    ◦ Sorted/hashed tables for lookups, BINARY SEARCH, field symbols over work areas, avoid nested loops (parallel cursor)
    ◦ DELETE ... WHERE instead of loop + delete, FREE large tables
4. Code pushdown (HANA) [A]
    ◦ Move logic to DB via CDS / AMDP, avoid data-to-code transfer
5. Parallel processing [A]
    ◦ CALL FUNCTION ... STARTING NEW TASK with server groups (RZ12), SPTA framework, background packaging
6. Memory management [A]
    ◦ Memory Inspector (S_MEMORY_INSPECTOR), shared objects (SHMA), sharing vs copying of tables
15. Modern ABAP (7.40 / 7.50+, S/4HANA, ABAP Cloud)
1. New syntax (7.40+) [I]
    ◦ Inline declarations DATA( ), FIELD-SYMBOL( )
    ◦ Constructor operators: NEW, VALUE, CORRESPONDING, CONV, CAST, REF, EXACT, COND, SWITCH, REDUCE, FILTER
    ◦ Table expressions, FOR iterations, LET, BASE, string templates with formatting options
    ◦ Predicate functions, xsdbool( ), boolc( )
2. ABAP CDS views [A]
    ◦ DDIC-based (DEFINE VIEW) vs CDS view entities (DEFINE VIEW ENTITY)
    ◦ Joins, associations & path expressions, CASE, CAST, built-in functions, aggregates
    ◦ Parameters, session variables, annotations (@AbapCatalog, @UI, @OData.publish, @Analytics)
    ◦ Access control (DCL, @AccessControl.authorizationCheck), table functions
    ◦ VDM layers: basic / interface (I_), composite, consumption (C_)
3. AMDP [A]
    ◦ IF_AMDP_MARKER_HDB, BY DATABASE PROCEDURE / FUNCTION, SQLScript basics, debugging AMDP
4. RAP (ABAP RESTful Application Programming Model) [A]
    ◦ Data model (CDS), behavior definition (BDEF), behavior pool, service definition & binding
    ◦ Managed vs unmanaged, draft handling, determinations, validations, actions, feature control
    ◦ EML: READ ENTITIES, MODIFY ENTITIES, COMMIT ENTITIES
    ◦ Fiori Elements preview, metadata extensions
5. ABAP Cloud & clean core [A]
    ◦ ABAP Cloud language version, released APIs (C1 contract), BTP ABAP Environment, embedded Steampunk
    ◦ Tier model (Tier 1/2/3), ATC cloud readiness checks
6. S/4HANA data model changes [A]
    ◦ MATDOC, ACDOCA, Business Partner (BP) replacing customer/vendor, simplified tables, compatibility views
7. Tooling [I]
    ◦ Eclipse ADT (mandatory for CDS/RAP), abapGit, ABAP Doc, quick fixes & refactoring
16. Key Transaction Codes
Area
T-codes
Development
SE80, SE38, SE37, SE24, SE11, SE51, SE41, SE93, SE91
DDIC & data
SE11, SE14, SE16N, SE54, SM30, SM34
Transports
SE09, SE10, SE01, STMS
Forms
SE71, SE78, SO10, SMARTFORMS, SMARTSTYLES, SFP, NACE, SPAD, SP01
Enhancements
SMOD, CMOD, SE18, SE19, SE20, SE84, SPAU, SPDD
Migration
SHDB, SM35, LSMW, LTMC, BAPI
Interfaces
SM59, SWO1, WE02, WE05, WE19, WE20, WE30, WE31, WE81, WE82, BD64, BD87, SEGW, SOAMANAGER, /IWFND/MAINT_SERVICE, /IWFND/GW_CLIENT
Debug & analysis
ST22, SM21, SLG1, SAAB, ST05, SAT, ST12, SM50, SM66, SM12, SM13
Jobs
SM36, SM37
Quality
SCI, ATC, SLIN, SE30