/*
 * Copyright 2026 Philterd, LLC.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package ai.philterd.phisql;

import org.junit.jupiter.api.Test;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.ObjectMapper;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Verifies that PhiSQL that parses successfully but cannot be compiled produces
 * a {@link Compiler.CompileException} with a useful message.
 */
class CompileErrorTest {

    private static final ObjectMapper MAPPER = new ObjectMapper();

    private static JsonNode json(CompileResult result) {
        return MAPPER.readTree(result.toJsonString());
    }

    @Test
    void rejectsUnknownEntityType() {
        Compiler compiler = new Compiler();
        Compiler.CompileException ex = assertThrows(
                Compiler.CompileException.class,
                () -> compiler.compile("REDACT NOT_AN_ENTITY WITH MASK;")
        );
        assertTrue(ex.getMessage().contains("NOT_AN_ENTITY"),
                "Expected error to name the unknown entity: " + ex.getMessage());
    }

    @Test
    void passesThroughUncataloguedStrategyArgument() {
        // An argument the strategy catalog does not list is no longer an error:
        // it passes through to the Phileas JSON by its schema property name, so
        // any strategy field (salt, condition, truncateDirection, ...) is settable.
        Compiler compiler = new Compiler();
        JsonNode strategy = json(compiler.compile("REDACT SSN WITH MASK(salt=TRUE);"))
                .path("identifiers").path("ssn")
                .path("ssnFilterStrategies").path(0);
        assertTrue(strategy.path("salt").asBoolean(),
                "Uncatalogued strategy arg should pass through to JSON: " + strategy);
    }

    @Test
    void rejectsInvalidEnumValue() {
        Compiler compiler = new Compiler();
        Compiler.CompileException ex = assertThrows(
                Compiler.CompileException.class,
                () -> compiler.compile("REDACT SSN WITH STATIC_REPLACE(value='X', scope=invalid);")
        );
        assertTrue(ex.getMessage().toLowerCase().contains("scope")
                        || ex.getMessage().toLowerCase().contains("invalid"),
                "Expected error to identify the invalid enum value: " + ex.getMessage());
    }

    @Test
    void rejectsDateOnlyStrategyOnNonDateEntity() {
        Compiler compiler = new Compiler();
        Compiler.CompileException ex = assertThrows(
                Compiler.CompileException.class,
                () -> compiler.compile("REDACT SSN WITH SHIFT(days=30);")
        );
        assertTrue(ex.getMessage().contains("SHIFT") && ex.getMessage().contains("date-only"),
                "Expected a date-only strategy error: " + ex.getMessage());
    }

    @Test
    void allowsDateOnlyStrategyOnDate() {
        // Positive control: a date-only strategy on DATE compiles.
        JsonNode strategy = json(new Compiler().compile("REDACT DATE WITH SHIFT(days=30);"))
                .path("identifiers").path("date")
                .path("dateFilterStrategies").path(0);
        assertTrue(strategy.path("strategy").asString().equals("SHIFT"),
                "DATE + SHIFT should compile: " + strategy);
    }

    @Test
    void rejectsStaticReplaceWithoutValue() {
        // The catalog marks STATIC_REPLACE's `value` required; omitting it is a
        // semantic error rather than a malformed strategy.
        Compiler compiler = new Compiler();
        Compiler.CompileException ex = assertThrows(
                Compiler.CompileException.class,
                () -> compiler.compile("REDACT SURNAME WITH STATIC_REPLACE(scope=document);")
        );
        assertTrue(ex.getMessage().contains("STATIC_REPLACE requires argument 'value'"),
                "Expected a required-argument error: " + ex.getMessage());
    }

    @Test
    void allowsStaticReplaceWithValue() {
        // Positive control: STATIC_REPLACE with a value compiles.
        JsonNode strategy = json(new Compiler().compile("REDACT SURNAME WITH STATIC_REPLACE(value='Customer');"))
                .path("identifiers").path("surname")
                .path("surnameFilterStrategies").path(0);
        assertTrue(strategy.path("staticReplacement").asString().equals("Customer"),
                "STATIC_REPLACE with value should compile: " + strategy);
    }

    @Test
    void rejectsDuplicateGeneratorName() {
        // Two DEFINE GENERATOR statements with the same name would collide in the
        // single name-keyed generators object; that is a semantic error.
        Compiler compiler = new Compiler();
        Compiler.CompileException ex = assertThrows(
                Compiler.CompileException.class,
                () -> compiler.compile(
                        "DEFINE GENERATOR 'g' TYPE 'ollama' OPTIONS (prompt = 'A: {{token}}', timeoutMs = 1000);\n"
                        + "DEFINE GENERATOR 'g' TYPE 'ollama' OPTIONS (prompt = 'B: {{token}}', timeoutMs = 1000);")
        );
        assertTrue(ex.getMessage().contains("Duplicate generator name"),
                "Expected a duplicate-generator error: " + ex.getMessage());
    }

    @Test
    void allowsTwoDistinctGenerators() {
        // Positive control: distinct names both land in the generators block.
        JsonNode generators = json(new Compiler().compile(
                "DEFINE GENERATOR 'a' TYPE 'ollama' OPTIONS (prompt = '{{token}}', timeoutMs = 1000);\n"
                + "DEFINE GENERATOR 'b' TYPE 'ollama' OPTIONS (prompt = '{{token}}', timeoutMs = 1000);"))
                .path("generators");
        assertTrue(generators.has("a") && generators.has("b"),
                "Both generators should be present: " + generators);
    }

    @Test
    void compilesReviewSamplingRate() {
        JsonNode review = json(new Compiler().compile(
                "REDACT SSN WITH MASK;\nCONFIGURE review (samplingRate = 0.10);"))
                .path("config").path("review");
        assertTrue(review.path("samplingRate").asDouble() == 0.1,
                "CONFIGURE REVIEW should write config.review: " + review);
    }

    @Test
    void reviewIsNotReserved() {
        // REVIEW is matched contextually, so it stays usable as an identifier.
        JsonNode policy = json(new Compiler().compile("POLICY review;\nREDACT SSN WITH MASK;"));
        assertTrue(policy.path("identifiers").has("ssn"), "POLICY review should compile: " + policy);
    }

    @Test
    void rejectsSamplingRateOutOfRange() {
        for (String rate : new String[] {"1.5", "-0.1", "'half'"}) {
            Compiler.CompileException ex = assertThrows(
                    Compiler.CompileException.class,
                    () -> new Compiler().compile(
                            "REDACT SSN WITH MASK;\nCONFIGURE REVIEW (samplingRate = " + rate + ");"));
            assertTrue(ex.getMessage().contains("samplingRate must be a number from 0.0 to 1.0"),
                    "Expected a samplingRate range error: " + ex.getMessage());
        }
    }

    @Test
    void rejectsUnknownConfigBlock() {
        Compiler.CompileException ex = assertThrows(
                Compiler.CompileException.class,
                () -> new Compiler().compile("REDACT SSN WITH MASK;\nCONFIGURE AUDIT (samplingRate = 0.1);"));
        assertTrue(ex.getMessage().contains("Unknown config block: AUDIT"),
                "Expected an unknown-block error: " + ex.getMessage());
    }

    @Test
    void compilesEmailConfig() {
        JsonNode email = json(new Compiler().compile(
                "REDACT SSN WITH MASK;\nCONFIGURE email (headers = (removeDate = TRUE, removeSubject = FALSE),"
                        + " attachments = 'redact', inlineImages = 'remove');"))
                .path("config").path("email");
        assertTrue(email.path("headers").path("removeDate").asBoolean()
                        && email.path("headers").has("removeSubject")
                        && email.path("attachments").asString().equals("redact")
                        && email.path("inlineImages").asString().equals("remove"),
                "CONFIGURE EMAIL should write config.email: " + email);
    }

    @Test
    void emailIsNotReserved() {
        JsonNode policy = json(new Compiler().compile("POLICY email;\nREDACT SSN WITH MASK;"));
        assertTrue(policy.path("identifiers").has("ssn"), "POLICY email should compile: " + policy);
    }

    @Test
    void rejectsInvalidEmailConfig() {
        String[][] cases = {
                {"attachment = 'remove'", "Unknown email setting: attachment"},
                {"headers = (removeBcc = TRUE)", "Unknown email header setting: removeBcc"},
                {"headers = (removeDate = 'yes')", "email header setting removeDate must be TRUE or FALSE"},
                {"headers = TRUE", "email headers must be a setting list"},
                {"attachments = 'strip'", "attachments must be one of keep, remove, redact"},
                {"attachments = TRUE", "attachments must be one of keep, remove, redact"},
                {"inlineImages = 'redact'", "inlineImages must be one of keep, remove"},
        };
        for (String[] c : cases) {
            Compiler.CompileException ex = assertThrows(
                    Compiler.CompileException.class,
                    () -> new Compiler().compile("REDACT SSN WITH MASK;\nCONFIGURE EMAIL (" + c[0] + ");"));
            assertTrue(ex.getMessage().contains(c[1]), "Expected '" + c[1] + "': " + ex.getMessage());
        }
    }

    @Test
    void compilesLeftoverCheck() {
        JsonNode review = json(new Compiler().compile(
                "REDACT SSN WITH MASK;\nCONFIGURE REVIEW (samplingRate = 0.1,"
                        + " leftoverCheck = (mode = 'always', using = 'samePolicy'));"))
                .path("config").path("review");
        assertTrue(review.path("samplingRate").asDouble() == 0.1
                        && review.path("leftoverCheck").path("mode").asString().equals("always")
                        && review.path("leftoverCheck").path("using").asString().equals("samePolicy"),
                "CONFIGURE REVIEW should write config.review.leftoverCheck: " + review);
    }

    @Test
    void rejectsInvalidLeftoverCheck() {
        String[][] cases = {
                {"leftoverCheck = TRUE", "leftoverCheck must be a setting list"},
                {"leftoverCheck = (depth = 'broad')", "Unknown leftoverCheck setting: depth"},
                {"leftoverCheck = (mode = 'sometimes')", "leftoverCheck mode must be one of off, onRequest, always"},
                {"leftoverCheck = (mode = 'onrequest')", "leftoverCheck mode must be one of off, onRequest, always"},
                {"leftoverCheck = (using = 'everything')", "leftoverCheck using must be one of broad, samePolicy"},
                {"leftoverCheck = (using = TRUE)", "leftoverCheck using must be one of broad, samePolicy"},
        };
        for (String[] c : cases) {
            Compiler.CompileException ex = assertThrows(
                    Compiler.CompileException.class,
                    () -> new Compiler().compile("REDACT SSN WITH MASK;\nCONFIGURE REVIEW (" + c[0] + ");"));
            assertTrue(ex.getMessage().contains(c[1]), "Expected '" + c[1] + "': " + ex.getMessage());
        }
    }

    @Test
    void compilesWordAndExcelConfig() {
        JsonNode config = json(new Compiler().compile(
                "REDACT SSN WITH MASK;\nCONFIGURE word (comments = 'redact', trackedChanges = 'redact',"
                        + " removeDocumentProperties = FALSE, highlight = TRUE);\n"
                        + "CONFIGURE Excel (formulaCaches = 'keep', uninspectableObjects = 'keep');"))
                .path("config");
        JsonNode word = config.path("word");
        JsonNode excel = config.path("excel");
        assertTrue(word.path("comments").asString().equals("redact")
                        && word.path("trackedChanges").asString().equals("redact")
                        && word.path("removeDocumentProperties").isBoolean()
                        && !word.path("removeDocumentProperties").asBoolean()
                        && word.path("highlight").asBoolean()
                        && word.size() == 4,
                "CONFIGURE WORD should write config.word: " + word);
        assertTrue(excel.path("formulaCaches").asString().equals("keep")
                        && excel.path("uninspectableObjects").asString().equals("keep")
                        && excel.size() == 2,
                "CONFIGURE EXCEL should write config.excel: " + excel);
    }

    @Test
    void wordAndExcelAreNotReserved() {
        JsonNode policy = json(new Compiler().compile("POLICY word;\nREDACT SSN WITH MASK;"));
        assertTrue(policy.path("identifiers").has("ssn"), "POLICY word should compile: " + policy);
        policy = json(new Compiler().compile("POLICY excel;\nREDACT SSN WITH MASK;"));
        assertTrue(policy.path("identifiers").has("ssn"), "POLICY excel should compile: " + policy);
    }

    @Test
    void rejectsInvalidWordAndExcelConfig() {
        String[][] cases = {
                {"WORD", "comment = 'remove'", "Unknown word setting: comment"},
                {"WORD", "comments = 'strip'", "word setting comments must be one of remove, redact"},
                {"WORD", "trackedChanges = 'reject'", "word setting trackedChanges must be one of accept, redact"},
                {"WORD", "headersFooters = TRUE", "word setting headersFooters must be one of redact, keep"},
                {"WORD", "highlight = 'yes'", "word setting highlight must be TRUE or FALSE"},
                {"EXCEL", "comments = 'remove'", "Unknown excel setting: comments"},
                {"EXCEL", "formulaCaches = 'remove'", "excel setting formulaCaches must be one of redact, keep"},
                {"EXCEL", "removeDocumentProperties = 1", "excel setting removeDocumentProperties must be TRUE or FALSE"},
        };
        for (String[] c : cases) {
            Compiler.CompileException ex = assertThrows(
                    Compiler.CompileException.class,
                    () -> new Compiler().compile(
                            "REDACT SSN WITH MASK;\nCONFIGURE " + c[0] + " (" + c[1] + ");"));
            assertTrue(ex.getMessage().contains(c[2]), "Expected '" + c[2] + "': " + ex.getMessage());
        }
    }

    @Test
    void compilesCsvAndTabularConfig() {
        // The filter column names emailAddress before the REDACT that defines it.
        JsonNode policy = json(new Compiler().compile("CONFIGURE csv (delimiter = ';', quote = '\\'');\nCONFIGURE Tabular Sheet (worksheet = 'Patients', unlistedColumns = 'redact', columns = [(header = 'SSN', action = 'redact', strategies = [(strategy = 'MASK')]), (index = 2, action = 'filter', filters = ['emailAddress'])]);\nREDACT EMAIL_ADDRESS WITH REDACT;"));
        JsonNode csv = policy.path("config").path("csv");
        assertTrue(csv.path("delimiter").asString().equals(";") && csv.path("quote").asString().equals("'"),
                "CONFIGURE CSV should write config.csv: " + csv);
        JsonNode sheets = policy.path("tabular").path("sheets");
        JsonNode columns = sheets.path(0).path("columns");
        assertTrue(sheets.size() == 1
                        && sheets.path(0).path("worksheet").asString().equals("Patients")
                        && sheets.path(0).path("unlistedColumns").asString().equals("redact")
                        && columns.path(0).path("strategies").path(0).path("strategy").asString().equals("MASK")
                        && columns.path(1).path("index").asInt() == 2
                        && columns.path(1).path("filters").path(0).asString().equals("emailAddress"),
                "CONFIGURE TABULAR SHEET should write tabular.sheets: " + sheets);
    }

    @Test
    void csvTabularAndSheetAreNotReserved() {
        for (String name : new String[] {"csv", "tabular", "sheet"}) {
            JsonNode policy = json(new Compiler().compile("POLICY " + name + ";\nREDACT SSN WITH MASK;"));
            assertTrue(policy.path("identifiers").has("ssn"), "POLICY " + name + " should compile: " + policy);
        }
    }

    @Test
    void rejectsInvalidCsvAndTabularConfig() {
        String[][] cases = {
                {"CONFIGURE TABULAR (headerRows = 1);", "Unknown config block: TABULAR"},
                {"CONFIGURE CSV (quote = '\\n');", "csv quote must be a single character other than a line break"},
                {"CONFIGURE CSV (encoding = '');", "csv encoding must be a non-empty string"},
                {"CONFIGURE TABULAR SHEET (headerRows = 1.5);", "tabular sheet headerRows must be a whole number of 0 or more"},
                {"CONFIGURE TABULAR SHEET (unlistedColumns = 'drop');", "tabular sheet unlistedColumns must be one of identifiers, ignore, redact"},
                {"CONFIGURE TABULAR SHEET (headerRows = 1);\nCONFIGURE TABULAR SHEET (headerRows = 2);", "More than one tabular sheet without a worksheet"},
                {"CONFIGURE TABULAR SHEET (columns = (header = 'SSN', action = 'ignore'));", "tabular sheet columns must be a list of column rules"},
                {"CONFIGURE TABULAR SHEET (columns = [(header = 'SSN', action = 'ignore', note = 'x')]);", "Unknown tabular column setting: note"},
                {"CONFIGURE TABULAR SHEET (columns = [(action = 'ignore')]);", "A tabular column rule needs exactly one of header or index"},
                {"CONFIGURE TABULAR SHEET (columns = [(index = 0, action = 'ignore')]);", "tabular column index must be a whole number of 1 or more"},
                {"CONFIGURE TABULAR SHEET (columns = [(header = 'SSN')]);", "A tabular column rule needs an action"},
                {"CONFIGURE TABULAR SHEET (columns = [(index = 3, action = 'ignore'), (index = 3, action = 'ignore')]);", "More than one column rule for index 3"},
                {"CONFIGURE TABULAR SHEET (columns = [(header = 'Notes', action = 'filter')]);", "A filter column rule needs filters"},
                {"CONFIGURE TABULAR SHEET (columns = [(header = 'Notes', action = 'filter', filters = ['emailAddress', 'emailAddress'])]);", "column filters must be a non-empty list of distinct identifiers names"},
                {"CONFIGURE TABULAR SHEET (columns = [(header = 'SSN', action = 'ignore', filters = ['emailAddress'])]);", "filters apply only to a filter column rule"},
                {"CONFIGURE TABULAR SHEET (columns = [(header = 'SSN', action = 'redact', strategies = (strategy = 'MASK'))]);", "column strategies must be a non-empty list of strategies"},
                {"CONFIGURE TABULAR SHEET (columns = [(header = 'SSN', action = 'redact', strategies = [(strategy = 'NOPE')])]);", "Unknown strategy in column strategies"},
                {"CONFIGURE TABULAR SHEET (unlistedColumns = 'redact', unlistedStrategies = [(strategy = 'MASK', condition = 'x')]);", "unlistedStrategies cannot have a condition"},
        };
        for (String[] c : cases) {
            Compiler.CompileException ex = assertThrows(
                    Compiler.CompileException.class,
                    () -> new Compiler().compile("REDACT EMAIL_ADDRESS WITH REDACT;\n" + c[0]),
                    c[0]);
            assertTrue(ex.getMessage().contains(c[1]), "Expected '" + c[1] + "': " + ex.getMessage());
        }
    }
}
