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

using System.Reflection;
using System.Text;

namespace Philterd.PhiSql;

/// <summary>
/// Reads the spec catalog and schema embedded into this assembly at build time
/// (see the EmbeddedResource items in PhiSql.csproj). This mirrors the Java
/// reference loading them from JAR resources and the Python reference loading
/// them from bundled package data, so the library is self-contained: a
/// dependent application needs no checked-out spec.
/// </summary>
internal static class Resources
{
    private static readonly Assembly Asm = typeof(Resources).Assembly;

    internal static string EntityTypesYaml() => Read("PhiSql.Data.catalog.entity-types.yaml");

    internal static string StrategiesYaml() => Read("PhiSql.Data.catalog.strategies.yaml");

    internal static string Schema(string version) => Read($"PhiSql.Data.schema.{version}.schema.json");

    private static string Read(string logicalName)
    {
        using Stream? stream = Asm.GetManifestResourceStream(logicalName);
        if (stream is null)
        {
            throw new InvalidOperationException(
                $"Embedded resource not found: {logicalName}. " +
                "Available: " + string.Join(", ", Asm.GetManifestResourceNames()));
        }
        using var reader = new StreamReader(stream, Encoding.UTF8);
        return reader.ReadToEnd();
    }
}
