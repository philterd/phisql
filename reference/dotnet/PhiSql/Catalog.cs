// Copyright 2026 Philterd, LLC.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

using YamlDotNet.Serialization;
using YamlDotNet.Serialization.NamingConventions;

namespace Philterd.PhiSql;

/// <summary>A named argument allowed on a strategy.</summary>
public sealed record StrategyArg(string Name, string? PhileasField, string? Type, IReadOnlyList<string> EnumValues);

/// <summary>Catalog entry for a filter strategy. <c>DateOnly</c> marks date-only strategies.</summary>
public sealed record Strategy(string Name, string PhileasEnum, IReadOnlyList<StrategyArg> Args, bool DateOnly = false)
{
    /// <summary>Returns the strategy argument with the given (case-insensitive) name, or null.</summary>
    public StrategyArg? FindArg(string? argName)
    {
        if (argName is null) return null;
        foreach (StrategyArg arg in Args)
            if (string.Equals(arg.Name, argName, StringComparison.OrdinalIgnoreCase))
                return arg;
        return null;
    }
}

/// <summary>Catalog entry for an entity type.</summary>
public sealed record EntityType(string Name, string PhileasField, string PhileasStrategiesField);

/// <summary>
/// In-memory view of the PhiSQL spec catalog YAML files. The catalog is the
/// single source of truth for entity types and strategies; the compiler is
/// driven entirely by it. Lookups by name are case-insensitive.
/// </summary>
public sealed class Catalog
{
    /// <summary>Catalog version (matches the spec version this catalog targets).</summary>
    public const string Version = "v1.0";

    private readonly IReadOnlyDictionary<string, EntityType> _entitiesByName;
    private readonly IReadOnlyDictionary<string, Strategy> _strategiesByName;

    private Catalog(IReadOnlyDictionary<string, EntityType> entities,
                    IReadOnlyDictionary<string, Strategy> strategies)
    {
        _entitiesByName = entities;
        _strategiesByName = strategies;
    }

    /// <summary>Loads the v1.0 catalog from the YAML embedded in this assembly.</summary>
    public static Catalog LoadDefault()
    {
        IDeserializer deserializer = new DeserializerBuilder()
            .WithNamingConvention(UnderscoredNamingConvention.Instance)
            .IgnoreUnmatchedProperties()
            .Build();

        var entities = new Dictionary<string, EntityType>(StringComparer.Ordinal);
        var entitiesFile = deserializer.Deserialize<EntityTypesFile>(Resources.EntityTypesYaml());
        foreach (EntityEntry e in entitiesFile.Entities ?? new())
        {
            var entity = new EntityType(e.Name!, e.PhileasField!, e.PhileasStrategiesField!);
            entities[entity.Name.ToUpperInvariant()] = entity;
        }

        var strategies = new Dictionary<string, Strategy>(StringComparer.Ordinal);
        var strategiesFile = deserializer.Deserialize<StrategiesFile>(Resources.StrategiesYaml());
        foreach (StrategyEntry s in strategiesFile.Strategies ?? new())
        {
            var args = new List<StrategyArg>();
            foreach (ArgEntry a in s.Args ?? new())
            {
                args.Add(new StrategyArg(a.Name!, a.PhileasField, a.Type,
                    a.EnumValues ?? new List<string>()));
            }
            var strategy = new Strategy(s.Name!, s.PhileasEnum!, args,
                s.PhileasStrategyDef == "dateFilterStrategy");
            strategies[strategy.Name.ToUpperInvariant()] = strategy;
        }

        return new Catalog(entities, strategies);
    }

    /// <summary>Returns the entity type with the given (case-insensitive) name, or null.</summary>
    public EntityType? GetEntity(string? name)
    {
        if (name is null) return null;
        return _entitiesByName.TryGetValue(name.ToUpperInvariant(), out EntityType? e) ? e : null;
    }

    /// <summary>Returns the strategy with the given (case-insensitive) name, or null.</summary>
    public Strategy? GetStrategy(string? name)
    {
        if (name is null) return null;
        return _strategiesByName.TryGetValue(name.ToUpperInvariant(), out Strategy? s) ? s : null;
    }

    /// <summary>The Phileas strategy enums classified date-only (dateFilterStrategy).</summary>
    public IReadOnlySet<string> DateOnlyStrategyEnums() =>
        _strategiesByName.Values.Where(s => s.DateOnly).Select(s => s.PhileasEnum).ToHashSet();

    /// <summary>The PhiSQL entity name for a Phileas identifier field, or null.</summary>
    public string? EntityNameForField(string field) =>
        _entitiesByName.Values.FirstOrDefault(e => e.PhileasField == field)?.Name;

    // --- YAML DTOs (snake_case via UnderscoredNamingConvention) ---------------

    private sealed class EntityTypesFile { public List<EntityEntry>? Entities { get; set; } }

    private sealed class EntityEntry
    {
        public string? Name { get; set; }
        public string? PhileasField { get; set; }
        public string? PhileasStrategiesField { get; set; }
    }

    private sealed class StrategiesFile { public List<StrategyEntry>? Strategies { get; set; } }

    private sealed class StrategyEntry
    {
        public string? Name { get; set; }
        public string? PhileasEnum { get; set; }
        public string? PhileasStrategyDef { get; set; }
        public List<ArgEntry>? Args { get; set; }
    }

    private sealed class ArgEntry
    {
        public string? Name { get; set; }
        public string? PhileasField { get; set; }
        public string? Type { get; set; }
        public List<string>? EnumValues { get; set; }
    }
}
