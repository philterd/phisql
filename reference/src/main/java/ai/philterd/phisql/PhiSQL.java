/*
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 */
package ai.philterd.phisql;

import ai.philterd.phisql.grammar.PhiSQLLexer;
import ai.philterd.phisql.grammar.PhiSQLParser;
import org.antlr.v4.runtime.BaseErrorListener;
import org.antlr.v4.runtime.CharStream;
import org.antlr.v4.runtime.CharStreams;
import org.antlr.v4.runtime.CommonTokenStream;
import org.antlr.v4.runtime.RecognitionException;
import org.antlr.v4.runtime.Recognizer;

import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

/**
 * Entry point for parsing PhiSQL source into an ANTLR parse tree.
 *
 * <p>Behavior is defined by the grammar at {@code spec/v0.1/grammar/PhiSQL.g4}
 * (the parser is generated from it at build time) and by the catalog files
 * under {@code spec/v0.1/catalog/} (consumed by the future compiler).
 */
public final class PhiSQL {

    private PhiSQL() {}

    /**
     * Parses PhiSQL source into a document parse tree.
     *
     * @throws ParseException on any syntax error, with all messages aggregated.
     */
    public static PhiSQLParser.DocumentContext parse(String source) {
        return parse(CharStreams.fromString(source));
    }

    /**
     * Parses PhiSQL source from an input stream into a document parse tree.
     */
    public static PhiSQLParser.DocumentContext parse(InputStream input) throws IOException {
        return parse(CharStreams.fromStream(input, StandardCharsets.UTF_8));
    }

    private static PhiSQLParser.DocumentContext parse(CharStream input) {
        PhiSQLLexer lexer = new PhiSQLLexer(input);
        CommonTokenStream tokens = new CommonTokenStream(lexer);
        PhiSQLParser parser = new PhiSQLParser(tokens);

        List<String> errors = new ArrayList<>();
        CollectingErrorListener listener = new CollectingErrorListener(errors);

        lexer.removeErrorListeners();
        lexer.addErrorListener(listener);
        parser.removeErrorListeners();
        parser.addErrorListener(listener);

        PhiSQLParser.DocumentContext tree = parser.document();

        if (!errors.isEmpty()) {
            throw new ParseException(String.join("\n", errors));
        }
        return tree;
    }

    private static final class CollectingErrorListener extends BaseErrorListener {
        private final List<String> errors;

        CollectingErrorListener(List<String> errors) {
            this.errors = errors;
        }

        @Override
        public void syntaxError(Recognizer<?, ?> recognizer,
                                Object offendingSymbol,
                                int line,
                                int charPositionInLine,
                                String msg,
                                RecognitionException e) {
            errors.add("line " + line + ":" + charPositionInLine + " " + msg);
        }
    }

    /** Thrown when PhiSQL source fails to parse. */
    public static final class ParseException extends RuntimeException {
        public ParseException(String message) {
            super(message);
        }
    }
}
