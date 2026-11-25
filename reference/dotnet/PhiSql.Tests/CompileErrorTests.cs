// Copyright 2026 Philterd, LLC.
//
// Licensed under the Apache License, Version 2.0 (the "License").
// See ../../../LICENSE.

using System.Text.Json.Nodes;
using Xunit;

namespace Philterd.PhiSql.Tests;

/// <summary>Verifies that well-formed-but-uncompilable PhiSQL throws CompileException.</summary>
public class CompileErrorTests
{
    [Fact]
    public void RejectsUnknownEntityType()
    {
        var ex = Assert.Throws<CompileException>(() => new Compiler().Compile("REDACT NOT_AN_ENTITY WITH MASK;"));
        Assert.Contains("NOT_AN_ENTITY", ex.Message);
    }

    [Fact]
    public void PassesThroughUncataloguedStrategyArgument()
    {
        JsonNode strategy = new Compiler().Compile("REDACT SSN WITH MASK(salt=TRUE);")
            .PolicyJson["identifiers"]!["ssn"]!["ssnFilterStrategies"]![0]!;
        Assert.True(strategy["salt"]!.GetValue<bool>());
    }

    [Fact]
    public void RejectsInvalidEnumValue()
    {
        var ex = Assert.Throws<CompileException>(
            () => new Compiler().Compile("REDACT SSN WITH STATIC_REPLACE(value='X', scope=invalid);"));
        string m = ex.Message.ToLowerInvariant();
        Assert.True(m.Contains("scope") || m.Contains("invalid"), ex.Message);
    }

    [Fact]
    public void RejectsDateOnlyStrategyOnNonDateEntity()
    {
        var ex = Assert.Throws<CompileException>(
            () => new Compiler().Compile("REDACT SSN WITH SHIFT(days=30);"));
        Assert.Contains("SHIFT", ex.Message);
        Assert.Contains("date-only", ex.Message);
    }

    [Fact]
    public void AllowsDateOnlyStrategyOnDate()
    {
        // Positive control: a date-only strategy on DATE compiles.
        JsonNode strategy = new Compiler().Compile("REDACT DATE WITH SHIFT(days=30);")
            .PolicyJson["identifiers"]!["date"]!["dateFilterStrategies"]![0]!;
        Assert.Equal("SHIFT", strategy["strategy"]!.GetValue<string>());
    }

    [Fact]
    public void RejectsStaticReplaceWithoutValue()
    {
        // The catalog marks STATIC_REPLACE's `value` required; omitting it is a
        // semantic error rather than a malformed strategy.
        var ex = Assert.Throws<CompileException>(
            () => new Compiler().Compile("REDACT SURNAME WITH STATIC_REPLACE(scope=document);"));
        Assert.Contains("STATIC_REPLACE requires argument 'value'", ex.Message);
    }

    [Fact]
    public void AllowsStaticReplaceWithValue()
    {
        // Positive control: STATIC_REPLACE with a value compiles.
        JsonNode strategy = new Compiler().Compile("REDACT SURNAME WITH STATIC_REPLACE(value='Customer');")
            .PolicyJson["identifiers"]!["surname"]!["surnameFilterStrategies"]![0]!;
        Assert.Equal("Customer", strategy["staticReplacement"]!.GetValue<string>());
    }

    [Fact]
    public void RejectsDuplicateGeneratorName()
    {
        // Two DEFINE GENERATOR statements with the same name would collide in the
        // single name-keyed generators object; that is a semantic error.
        var ex = Assert.Throws<CompileException>(() => new Compiler().Compile(
            "DEFINE GENERATOR 'g' TYPE 'ollama' OPTIONS (prompt = 'A: {{token}}', timeoutMs = 1000);\n" +
            "DEFINE GENERATOR 'g' TYPE 'ollama' OPTIONS (prompt = 'B: {{token}}', timeoutMs = 1000);"));
        Assert.Contains("Duplicate generator name", ex.Message);
    }

    [Fact]
    public void AllowsTwoDistinctGenerators()
    {
        // Positive control: distinct names both land in the generators block.
        JsonNode generators = new Compiler().Compile(
            "DEFINE GENERATOR 'a' TYPE 'ollama' OPTIONS (prompt = '{{token}}', timeoutMs = 1000);\n" +
            "DEFINE GENERATOR 'b' TYPE 'ollama' OPTIONS (prompt = '{{token}}', timeoutMs = 1000);")
            .PolicyJson["generators"]!;
        Assert.NotNull(generators["a"]);
        Assert.NotNull(generators["b"]);
    }

    [Fact]
    public void CompilesReviewSamplingRate()
    {
        var review = new Compiler().Compile("REDACT SSN WITH MASK;\nCONFIGURE review (samplingRate = 0.10);")
            .PolicyJson["config"]!["review"]!;
        Assert.Equal(0.1, review["samplingRate"]!.GetValue<double>());
    }

    [Fact]
    public void ReviewIsNotReserved()
    {
        // REVIEW is matched contextually, so it stays usable as an identifier.
        var policy = new Compiler().Compile("POLICY review;\nREDACT SSN WITH MASK;").PolicyJson;
        Assert.NotNull(policy["identifiers"]!["ssn"]);
    }

    [Theory]
    [InlineData("1.5")]
    [InlineData("-0.1")]
    [InlineData("2")]
    [InlineData("'half'")]
    [InlineData("TRUE")]
    public void RejectsSamplingRateOutOfRange(string rate)
    {
        var ex = Assert.Throws<CompileException>(() => new Compiler().Compile(
            "REDACT SSN WITH MASK;\nCONFIGURE REVIEW (samplingRate = " + rate + ");"));
        Assert.Contains("samplingRate must be a number from 0.0 to 1.0", ex.Message);
    }

    [Fact]
    public void AcceptsIntegerSamplingRate()
    {
        var review = new Compiler().Compile("REDACT SSN WITH MASK;\nCONFIGURE REVIEW (samplingRate = 1);")
            .PolicyJson["config"]!["review"]!;
        Assert.Equal(1, review["samplingRate"]!.GetValue<long>());
    }

    [Fact]
    public void RejectsUnknownConfigBlock()
    {
        var ex = Assert.Throws<CompileException>(() => new Compiler().Compile(
            "REDACT SSN WITH MASK;\nCONFIGURE AUDIT (samplingRate = 0.1);"));
        Assert.Contains("Unknown config block: AUDIT", ex.Message);
    }

    [Fact]
    public void CompilesEmailConfig()
    {
        var email = new Compiler().Compile(
                "REDACT SSN WITH MASK;\nCONFIGURE email (headers = (removeDate = TRUE, removeSubject = FALSE),"
                + " attachments = 'redact', inlineImages = 'remove');")
            .PolicyJson["config"]!["email"]!;
        Assert.True(email["headers"]!["removeDate"]!.GetValue<bool>());
        Assert.False(email["headers"]!["removeSubject"]!.GetValue<bool>());
        Assert.Equal("redact", email["attachments"]!.GetValue<string>());
        Assert.Equal("remove", email["inlineImages"]!.GetValue<string>());
    }

    [Fact]
    public void EmailIsNotReserved()
    {
        var policy = new Compiler().Compile("POLICY email;\nREDACT SSN WITH MASK;").PolicyJson;
        Assert.NotNull(policy["identifiers"]!["ssn"]);
    }

    [Theory]
    [InlineData("attachment = 'remove'", "Unknown email setting: attachment")]
    [InlineData("headers = (removeBcc = TRUE)", "Unknown email header setting: removeBcc")]
    [InlineData("headers = (removeDate = 'yes')", "email header setting removeDate must be TRUE or FALSE")]
    [InlineData("headers = TRUE", "email headers must be a setting list")]
    [InlineData("attachments = 'strip'", "attachments must be one of keep, remove, redact")]
    [InlineData("attachments = TRUE", "attachments must be one of keep, remove, redact")]
    [InlineData("inlineImages = 'redact'", "inlineImages must be one of keep, remove")]
    public void RejectsInvalidEmailConfig(string settings, string message)
    {
        var ex = Assert.Throws<CompileException>(() => new Compiler().Compile(
            "REDACT SSN WITH MASK;\nCONFIGURE EMAIL (" + settings + ");"));
        Assert.Contains(message, ex.Message);
    }

    [Fact]
    public void CompilesLeftoverCheck()
    {
        var review = new Compiler().Compile(
                "REDACT SSN WITH MASK;\nCONFIGURE REVIEW (samplingRate = 0.1,"
                + " leftoverCheck = (mode = 'always', using = 'samePolicy'));")
            .PolicyJson["config"]!["review"]!;
        Assert.Equal(0.1, review["samplingRate"]!.GetValue<double>());
        Assert.Equal("always", review["leftoverCheck"]!["mode"]!.GetValue<string>());
        Assert.Equal("samePolicy", review["leftoverCheck"]!["using"]!.GetValue<string>());
    }

    [Theory]
    [InlineData("leftoverCheck = TRUE", "leftoverCheck must be a setting list")]
    [InlineData("leftoverCheck = (depth = 'broad')", "Unknown leftoverCheck setting: depth")]
    [InlineData("leftoverCheck = (mode = 'sometimes')", "leftoverCheck mode must be one of off, onRequest, always")]
    [InlineData("leftoverCheck = (mode = 'onrequest')", "leftoverCheck mode must be one of off, onRequest, always")]
    [InlineData("leftoverCheck = (using = 'everything')", "leftoverCheck using must be one of broad, samePolicy")]
    [InlineData("leftoverCheck = (using = TRUE)", "leftoverCheck using must be one of broad, samePolicy")]
    public void RejectsInvalidLeftoverCheck(string settings, string message)
    {
        var ex = Assert.Throws<CompileException>(() => new Compiler().Compile(
            "REDACT SSN WITH MASK;\nCONFIGURE REVIEW (" + settings + ");"));
        Assert.Contains(message, ex.Message);
    }

    [Fact]
    public void CompilesWordAndExcelConfig()
    {
        var config = new Compiler().Compile(
                "REDACT SSN WITH MASK;\nCONFIGURE word (comments = 'redact', trackedChanges = 'redact',"
                + " removeDocumentProperties = FALSE, highlight = TRUE);\n"
                + "CONFIGURE Excel (formulaCaches = 'keep', uninspectableObjects = 'keep');")
            .PolicyJson["config"]!;
        var word = config["word"]!.AsObject();
        Assert.Equal("redact", word["comments"]!.GetValue<string>());
        Assert.Equal("redact", word["trackedChanges"]!.GetValue<string>());
        Assert.False(word["removeDocumentProperties"]!.GetValue<bool>());
        Assert.True(word["highlight"]!.GetValue<bool>());
        Assert.Equal(4, word.Count);
        var excel = config["excel"]!.AsObject();
        Assert.Equal("keep", excel["formulaCaches"]!.GetValue<string>());
        Assert.Equal("keep", excel["uninspectableObjects"]!.GetValue<string>());
        Assert.Equal(2, excel.Count);
    }

    [Theory]
    [InlineData("word")]
    [InlineData("excel")]
    public void WordAndExcelAreNotReserved(string name)
    {
        var policy = new Compiler().Compile("POLICY " + name + ";\nREDACT SSN WITH MASK;").PolicyJson;
        Assert.NotNull(policy["identifiers"]!["ssn"]);
    }

    [Theory]
    [InlineData("WORD", "comment = 'remove'", "Unknown word setting: comment")]
    [InlineData("WORD", "comments = 'strip'", "word setting comments must be one of remove, redact")]
    [InlineData("WORD", "trackedChanges = 'reject'", "word setting trackedChanges must be one of accept, redact")]
    [InlineData("WORD", "headersFooters = TRUE", "word setting headersFooters must be one of redact, keep")]
    [InlineData("WORD", "highlight = 'yes'", "word setting highlight must be TRUE or FALSE")]
    [InlineData("EXCEL", "comments = 'remove'", "Unknown excel setting: comments")]
    [InlineData("EXCEL", "formulaCaches = 'remove'", "excel setting formulaCaches must be one of redact, keep")]
    [InlineData("EXCEL", "removeDocumentProperties = 1", "excel setting removeDocumentProperties must be TRUE or FALSE")]
    public void RejectsInvalidWordAndExcelConfig(string block, string settings, string message)
    {
        var ex = Assert.Throws<CompileException>(() => new Compiler().Compile(
            "REDACT SSN WITH MASK;\nCONFIGURE " + block + " (" + settings + ");"));
        Assert.Contains(message, ex.Message);
    }

    [Fact]
    public void CompilesCsvAndTabularConfig()
    {
        // The filter column names emailAddress before the REDACT that defines it.
        var policy = new Compiler().Compile("CONFIGURE csv (delimiter = ';', quote = '\\'');\nCONFIGURE Tabular Sheet (worksheet = 'Patients', unlistedColumns = 'redact', columns = [(header = 'SSN', action = 'redact', strategies = [(strategy = 'MASK')]), (index = 2, action = 'filter', filters = ['emailAddress'])]);\nREDACT EMAIL_ADDRESS WITH REDACT;").PolicyJson;
        Assert.Equal(";", policy["config"]!["csv"]!["delimiter"]!.GetValue<string>());
        Assert.Equal("'", policy["config"]!["csv"]!["quote"]!.GetValue<string>());
        var sheets = policy["tabular"]!["sheets"]!.AsArray();
        Assert.Single(sheets);
        Assert.Equal("Patients", sheets[0]!["worksheet"]!.GetValue<string>());
        Assert.Equal("redact", sheets[0]!["unlistedColumns"]!.GetValue<string>());
        var columns = sheets[0]!["columns"]!.AsArray();
        Assert.Equal("MASK", columns[0]!["strategies"]![0]!["strategy"]!.GetValue<string>());
        Assert.Equal(2, columns[1]!["index"]!.GetValue<long>());
        Assert.Equal("emailAddress", columns[1]!["filters"]![0]!.GetValue<string>());
    }

    [Theory]
    [InlineData("csv")]
    [InlineData("tabular")]
    [InlineData("sheet")]
    public void CsvTabularAndSheetAreNotReserved(string name)
    {
        var policy = new Compiler().Compile("POLICY " + name + ";\nREDACT SSN WITH MASK;").PolicyJson;
        Assert.NotNull(policy["identifiers"]!["ssn"]);
    }

    [Theory]
    [InlineData("CONFIGURE TABULAR (headerRows = 1);", "Unknown config block: TABULAR")]
    [InlineData("CONFIGURE CSV (quote = '\\n');", "csv quote must be a single character other than a line break")]
    [InlineData("CONFIGURE CSV (encoding = '');", "csv encoding must be a non-empty string")]
    [InlineData("CONFIGURE TABULAR SHEET (headerRows = 1.5);", "tabular sheet headerRows must be a whole number of 0 or more")]
    [InlineData("CONFIGURE TABULAR SHEET (unlistedColumns = 'drop');", "tabular sheet unlistedColumns must be one of identifiers, ignore, redact")]
    [InlineData("CONFIGURE TABULAR SHEET (headerRows = 1);\nCONFIGURE TABULAR SHEET (headerRows = 2);", "More than one tabular sheet without a worksheet")]
    [InlineData("CONFIGURE TABULAR SHEET (columns = (header = 'SSN', action = 'ignore'));", "tabular sheet columns must be a list of column rules")]
    [InlineData("CONFIGURE TABULAR SHEET (columns = [(header = 'SSN', action = 'ignore', note = 'x')]);", "Unknown tabular column setting: note")]
    [InlineData("CONFIGURE TABULAR SHEET (columns = [(action = 'ignore')]);", "A tabular column rule needs exactly one of header or index")]
    [InlineData("CONFIGURE TABULAR SHEET (columns = [(index = 0, action = 'ignore')]);", "tabular column index must be a whole number of 1 or more")]
    [InlineData("CONFIGURE TABULAR SHEET (columns = [(header = 'SSN')]);", "A tabular column rule needs an action")]
    [InlineData("CONFIGURE TABULAR SHEET (columns = [(index = 3, action = 'ignore'), (index = 3, action = 'ignore')]);", "More than one column rule for index 3")]
    [InlineData("CONFIGURE TABULAR SHEET (columns = [(header = 'Notes', action = 'filter')]);", "A filter column rule needs filters")]
    [InlineData("CONFIGURE TABULAR SHEET (columns = [(header = 'Notes', action = 'filter', filters = ['emailAddress', 'emailAddress'])]);", "column filters must be a non-empty list of distinct identifiers names")]
    [InlineData("CONFIGURE TABULAR SHEET (columns = [(header = 'SSN', action = 'ignore', filters = ['emailAddress'])]);", "filters apply only to a filter column rule")]
    [InlineData("CONFIGURE TABULAR SHEET (columns = [(header = 'SSN', action = 'redact', strategies = (strategy = 'MASK'))]);", "column strategies must be a non-empty list of strategies")]
    [InlineData("CONFIGURE TABULAR SHEET (columns = [(header = 'SSN', action = 'redact', strategies = [(strategy = 'NOPE')])]);", "Unknown strategy in column strategies")]
    [InlineData("CONFIGURE TABULAR SHEET (unlistedColumns = 'redact', unlistedStrategies = [(strategy = 'MASK', condition = 'x')]);", "unlistedStrategies cannot have a condition")]
    public void RejectsInvalidCsvAndTabularConfig(string statements, string message)
    {
        var ex = Assert.Throws<CompileException>(() => new Compiler().Compile(
            "REDACT EMAIL_ADDRESS WITH REDACT;\n" + statements));
        Assert.Contains(message, ex.Message);
    }
}
