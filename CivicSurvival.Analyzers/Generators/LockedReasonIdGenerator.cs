using System;
using System.Collections.Generic;
using System.Collections.Immutable;
using System.Linq;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.CodeAnalysis.Text;

namespace CivicSurvival.Analyzers.Generators;

[Generator]
public class LockedReasonIdGenerator : IIncrementalGenerator
{
    public void Initialize(IncrementalGeneratorInitializationContext context)
    {
        var classDeclarations = context.SyntaxProvider
            .CreateSyntaxProvider(
                predicate: static (node, _) => IsSerializableDto(node),
                transform: static (ctx, _) => GetClassInfo(ctx))
            .Where(static info => info != null);

        var compilation = context.CompilationProvider;

        context.RegisterSourceOutput(
            classDeclarations.Combine(compilation),
            static (ctx, source) => Execute(ctx, source.Left, source.Right));
    }

    private static bool IsSerializableDto(SyntaxNode node)
    {
        return node is ClassDeclarationSyntax classDecl &&
               classDecl.AttributeLists.Count > 0;
    }

    private static ClassInfo? GetClassInfo(GeneratorSyntaxContext context)
    {
        var classDecl = (ClassDeclarationSyntax)context.Node;
        var semanticModel = context.SemanticModel;

        var classSymbol = semanticModel.GetDeclaredSymbol(classDecl);
        if (classSymbol == null)
            return null;

        var hasLockedReasonId = classSymbol.GetAttributes()
            .Any(a => a.AttributeClass?.Name == "LockedReasonIdAttribute" ||
                      a.AttributeClass?.ToDisplayString() == "CivicSurvival.Core.Attributes.LockedReasonIdAttribute");

        if (!hasLockedReasonId)
            return null;

        var properties = classSymbol.GetMembers()
            .OfType<IPropertySymbol>()
            .Select(p => (p.Name, p.Type.ToString()))
            .ToImmutableArray();

        return new ClassInfo(
            classSymbol.ContainingNamespace.ToDisplayString(),
            classSymbol.Name,
            classSymbol.TypeParameters.Select(t => t.Name).ToImmutableArray(),
            properties);
    }

    private static void Execute(SourceProductionContext context, ClassInfo? info, Compilation compilation)
    {
        if (info == null)
            return;

        var source = GenerateLockedReasonIdClass(info);
        context.AddSource($"{info.Name}_LockedReasonId.g.cs", SourceText.From(source, System.Text.Encoding.UTF8));
    }

    private static string GenerateLockedReasonIdClass(ClassInfo info)
    {
        var className = $"{info.Name}LockedReasonId";
        var namespaceName = info.Namespace;
        var typeParams = info.TypeParameters.Length > 0 ? $"<{string.Join(", ", info.TypeParameters)}>" : "";
        var typeConstraints = info.TypeParameters.Length > 0 ? $" where {string.Join(" where ", info.TypeParameters.Select(t => $"{t} : class"))}" : "";

        var sb = new System.Text.StringBuilder();
        sb.AppendLine("// GENERATED - DO NOT EDIT");
        sb.AppendLine($"// Source: {info.Name}");
        sb.AppendLine($"// Generator: CivicSurvival.Analyzers.LockedReasonIdGenerator");
        sb.AppendLine($"// GeneratedAt: {DateTime.UtcNow:yyyy-MM-ddTHH:mm:ssZ}");
        sb.AppendLine();
        sb.AppendLine("using System;");
        sb.AppendLine("using System.Collections.Generic;");
        sb.AppendLine();
        sb.AppendLine($"namespace {namespaceName}");
        sb.AppendLine("{");
        sb.AppendLine($"    /// <summary>");
        sb.AppendLine($"    /// Locked reason identifier property for {info.Name}.");
        sb.AppendLine($"    /// </summary>");
        sb.AppendLine($"    public static class {className}{typeParams}{typeConstraints}");
        sb.AppendLine("    {");
        sb.AppendLine($"        /// <summary>Default locked reason identifier.</summary>");
        sb.AppendLine($"        public const string Default = \"UNLOCKED\";");
        sb.AppendLine($"        /// <summary>Locked reason identifier for {info.Name}.</summary>");
        sb.AppendLine($"        public static string GetLockedReasonId({info.Name}{typeParams} instance) => Default;");
        sb.AppendLine($"        /// <summary>Sets the locked reason identifier on {info.Name}.</summary>");
        sb.AppendLine($"        public static void SetLockedReasonId({info.Name}{typeParams} instance, string reasonId) {{ /* No-op: reason stored in instance */ }}");
        sb.AppendLine("    }");
        sb.AppendLine("}");

        return sb.ToString();
    }

    private record ClassInfo(
        string Namespace,
        string Name,
        ImmutableArray<string> TypeParameters,
        ImmutableArray<(string Name, string Type)> Properties);
}