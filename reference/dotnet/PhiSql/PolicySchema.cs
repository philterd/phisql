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

using System.Text.Json.Nodes;

namespace Philterd.PhiSql;

/// <summary>
/// Access to the canonical redaction policy JSON Schema bundled in this
/// assembly. An application that depends on Philterd.PhiSql can read the schema
/// straight from the library — no network fetch, no separate checkout — exactly
/// as the Java reference exposes it through
/// <c>ai.philterd.phisql.PolicySchema</c> and the Python reference through
/// <c>phisql.PolicySchema</c>.
///
/// <code>
/// PolicySchema.GetSupportedSchemaVersion(); // "1.0.0"
/// PolicySchema.GetSchema();                  // the schema as a JSON string
/// PolicySchema.GetSchemaJson();              // the schema parsed to a JsonNode
/// </code>
/// </summary>
public static class PolicySchema
{
    /// <summary>
    /// Version of the canonical redaction policy schema this implementation
    /// targets. Selected at build time by the <c>SchemaVersion</c> MSBuild
    /// property in PhiSql.csproj; keep this constant in sync with it.
    /// </summary>
    public const string SupportedSchemaVersion = "1.0.0";

    /// <summary>Returns the version of the bundled schema, e.g. <c>"1.0.0"</c>.</summary>
    public static string GetSupportedSchemaVersion() => SupportedSchemaVersion;

    /// <summary>Returns the full bundled schema as a JSON string.</summary>
    public static string GetSchema() => Resources.Schema(SupportedSchemaVersion);

    /// <summary>Returns the bundled schema parsed into a <see cref="JsonNode"/>.</summary>
    public static JsonNode GetSchemaJson() => JsonNode.Parse(GetSchema())!;
}
