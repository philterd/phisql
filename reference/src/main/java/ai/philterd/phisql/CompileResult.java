/*
 * Licensed under the Apache License, Version 2.0 (the "License");
 */
package ai.philterd.phisql;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectWriter;
import com.fasterxml.jackson.databind.node.ObjectNode;

/**
 * Result of compiling a PhiSQL document.
 *
 * <p>{@link #policyName()} is the name from the {@code POLICY} declaration, which
 * implementations should use as the output filename ({@code <name>.json}).
 *
 * <p>{@link #description()} is the {@code DESCRIPTION '...'} text, which the
 * spec says belongs in a sibling {@code <name>.md} file. The compiler does
 * not write files; that is the caller's choice.
 *
 * <p>{@link #policyJson()} is the compiled Phileas JSON policy.
 */
public final class CompileResult {

    private static final ObjectMapper MAPPER = new ObjectMapper();
    private static final ObjectWriter PRETTY = MAPPER.writerWithDefaultPrettyPrinter();

    private final String policyName;
    private final String description;
    private final ObjectNode policyJson;

    public CompileResult(String policyName, String description, ObjectNode policyJson) {
        this.policyName = policyName;
        this.description = description;
        this.policyJson = policyJson;
    }

    public String policyName() {
        return policyName;
    }

    public String description() {
        return description;
    }

    public ObjectNode policyJson() {
        return policyJson;
    }

    /** Returns the policy JSON as a pretty-printed string. */
    public String toJsonString() {
        try {
            return PRETTY.writeValueAsString(policyJson);
        } catch (JsonProcessingException e) {
            throw new IllegalStateException("Failed to serialize compiled policy", e);
        }
    }
}
