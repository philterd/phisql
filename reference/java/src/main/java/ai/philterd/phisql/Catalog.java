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

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLMapper;

import java.io.IOException;
import java.io.InputStream;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * In-memory view of the PhiSQL spec catalog YAML files. The catalog files are
 * the single source of truth for entity types, strategies, keywords, and
 * predicate forms. They are packaged inside this JAR by the build, so the
 * compiler does not depend on the spec being checked out at runtime.
 *
 * <p>Lookups by name are case-insensitive, matching the language spec.
 */
public final class Catalog {

    /** Catalog version (matches the spec version this catalog targets). */
    public static final String VERSION = "v1.0";

    private static final String RESOURCE_PREFIX = "/spec/v1.0/catalog/";

    private final Map<String, EntityType> entitiesByName;
    private final Map<String, Strategy> strategiesByName;

    private Catalog(Map<String, EntityType> entitiesByName,
                    Map<String, Strategy> strategiesByName) {
        this.entitiesByName = entitiesByName;
        this.strategiesByName = strategiesByName;
    }

    /** Loads the v1.0 catalog from JAR resources. */
    public static Catalog loadDefault() {
        try {
            return load(RESOURCE_PREFIX);
        } catch (IOException e) {
            throw new IllegalStateException("Failed to load PhiSQL catalog", e);
        }
    }

    private static Catalog load(String prefix) throws IOException {
        YAMLMapper yaml = (YAMLMapper) new YAMLMapper().findAndRegisterModules();
        ObjectMapper mapper = (ObjectMapper) yaml;

        Map<String, EntityType> entities = new LinkedHashMap<>();
        try (InputStream in = open(prefix + "entity-types.yaml")) {
            Map<?, ?> root = mapper.readValue(in, Map.class);
            List<?> list = (List<?>) root.get("entities");
            for (Object item : list) {
                Map<?, ?> m = (Map<?, ?>) item;
                EntityType e = new EntityType(
                        (String) m.get("name"),
                        (String) m.get("phileas_field"),
                        (String) m.get("phileas_strategies_field")
                );
                entities.put(e.name().toUpperCase(Locale.ROOT), e);
            }
        }

        Map<String, Strategy> strategies = new LinkedHashMap<>();
        try (InputStream in = open(prefix + "strategies.yaml")) {
            Map<?, ?> root = mapper.readValue(in, Map.class);
            List<?> list = (List<?>) root.get("strategies");
            for (Object item : list) {
                Map<?, ?> m = (Map<?, ?>) item;
                List<StrategyArg> args = new java.util.ArrayList<>();
                Object rawArgs = m.get("args");
                if (rawArgs instanceof List<?> rawList) {
                    for (Object argItem : rawList) {
                        Map<?, ?> a = (Map<?, ?>) argItem;
                        @SuppressWarnings("unchecked")
                        List<String> enumValues = (List<String>) a.get("enum_values");
                        args.add(new StrategyArg(
                                (String) a.get("name"),
                                (String) a.get("phileas_field"),
                                (String) a.get("type"),
                                enumValues == null ? Collections.emptyList() : enumValues
                        ));
                    }
                }
                Strategy s = new Strategy(
                        (String) m.get("name"),
                        (String) m.get("phileas_enum"),
                        Collections.unmodifiableList(args),
                        "dateFilterStrategy".equals(m.get("phileas_strategy_def"))
                );
                strategies.put(s.name().toUpperCase(Locale.ROOT), s);
            }
        }

        return new Catalog(
                Collections.unmodifiableMap(entities),
                Collections.unmodifiableMap(strategies)
        );
    }

    private static InputStream open(String resource) {
        InputStream in = Catalog.class.getResourceAsStream(resource);
        if (in == null) {
            throw new IllegalStateException("Catalog resource not found: " + resource);
        }
        return in;
    }

    /** Returns the entity type with the given (case-insensitive) name, or null if unknown. */
    public EntityType getEntity(String name) {
        if (name == null) return null;
        return entitiesByName.get(name.toUpperCase(Locale.ROOT));
    }

    /** Returns the strategy with the given (case-insensitive) name, or null if unknown. */
    public Strategy getStrategy(String name) {
        if (name == null) return null;
        return strategiesByName.get(name.toUpperCase(Locale.ROOT));
    }

    /** The Phileas strategy enums classified date-only (dateFilterStrategy). */
    public java.util.Set<String> dateOnlyStrategyEnums() {
        java.util.Set<String> out = new java.util.HashSet<>();
        for (Strategy s : strategiesByName.values()) {
            if (s.dateOnly()) out.add(s.phileasEnum());
        }
        return out;
    }

    /** The PhiSQL entity name for a Phileas identifier field, or null if unknown. */
    public String entityNameForField(String field) {
        for (EntityType e : entitiesByName.values()) {
            if (e.phileasField().equals(field)) return e.name();
        }
        return null;
    }

    /** Catalog entry for an entity type. */
    public record EntityType(String name, String phileasField, String phileasStrategiesField) {}

    /** Catalog entry for a filter strategy. {@code dateOnly} marks date-only strategies. */
    public record Strategy(String name, String phileasEnum, List<StrategyArg> args, boolean dateOnly) {
        /** Returns the strategy argument with the given name, or null. */
        public StrategyArg findArg(String argName) {
            if (argName == null) return null;
            for (StrategyArg a : args) {
                if (a.name().equalsIgnoreCase(argName)) return a;
            }
            return null;
        }
    }

    /** A named argument allowed on a strategy. */
    public record StrategyArg(String name, String phileasField, String type, List<String> enumValues) {}
}
