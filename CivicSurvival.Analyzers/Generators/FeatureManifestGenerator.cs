using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.CodeAnalysis.Text;
namespace CivicSurvival.Analyzers.Generators;

public record FeatureAttributeInfo(string Name, string Id);

[Generator]
public class FeatureManifestGenerator : IIncrementalGenerator
{
    public void Initialize(IncrementalGeneratorInitializationContext context)
    {
        var featureAttributes = context.SyntaxProvider
            .CreateSyntaxProvider(
                predicate: static (node, _) => IsFeatureAttribute(node),
                transform: static (ctx, _) => GetFeatureAttributeInfo(ctx))
            .Where(static info => info != null);

        var compilation = context.CompilationProvider;

        context.RegisterSourceOutput(
            featureAttributes.Combine(compilation),
            static (ctx, source) => Execute(ctx, source.Left, source.Right));
    }

    private static bool IsFeatureAttribute(SyntaxNode node)
    {
        return node is AttributeSyntax attribute &&
               attribute.Name?.ToString() == "Feature" &&
               attribute.Name?.Parent?.Parent is AttributeListSyntax attributeList &&
               attributeList.Parent is ClassDeclarationSyntax classDecl &&
               classDecl.Identifier.Text == "FeatureAttribute";
    }

    private static FeatureAttributeInfo? GetFeatureAttributeInfo(GeneratorSyntaxContext context)
    {
        var attribute = (AttributeSyntax)context.Node;
        var semanticModel = context.SemanticModel;

        // Find the class that contains this attribute
        var classDeclaration = attribute?.Parent?.Parent?.Parent as ClassDeclarationSyntax;
        if (classDeclaration == null)
            return null;

        var className = classDeclaration.Identifier.Text;
        if (className != "FeatureAttribute")
            return null;

        // Extract arguments
        var args = attribute.ArgumentList?.Arguments;
        if (args == null || args.Value.Count < 2)
            return null;

        var nameExpr = args.Value[0];
        var idExpr = args.Value[1];

        string name = nameExpr.Expression?.ToString() ?? "";
        string id = idExpr.Expression?.ToString() ?? "";

        return new FeatureAttributeInfo(name, id);
    }

    private static void Execute(SourceProductionContext context, FeatureAttributeInfo? info, Compilation compilation)
    {
        if (info == null)
            return;

        var source = GenerateFeatureManifestClass(info);
        context.AddSource($"GeneratedFeature{info.Id}.g.cs", SourceText.From(source, System.Text.Encoding.UTF8));
    }

    private static string GenerateFeatureManifestClass(FeatureAttributeInfo info)
    {
        var className = $"GeneratedFeature{info.Id}";

        var sb = new System.Text.StringBuilder();
        sb.AppendLine("// GENERATED - DO NOT EDIT");
        sb.AppendLine($"// Source: Feature attribute {info.Name}");
        sb.AppendLine($"// Generator: CivicSurvival.Analyzers.FeatureManifestGenerator");
        sb.AppendLine($"// GeneratedAt: {DateTime.UtcNow:yyyy-MM-ddTHH:mm:ssZ}");
        sb.AppendLine();

        sb.AppendLine("using System;");
        sb.AppendLine();
        sb.AppendLine($"namespace CivicSurvival.Core.Features");
        sb.AppendLine("{");
        sb.AppendLine($"    /// <summary>");
        sb.AppendLine($"    /// Feature manifest entry for {info.Name}.");
        sb.AppendLine($"    /// This class is generated from the Feature attribute.");
        sb.AppendLine($"    /// </summary>");
        sb.AppendLine($"    public static class {className}");
        sb.AppendLine("    {");
        sb.AppendLine($"        /// <summary>Feature name</summary>");
        sb.AppendLine($"        public const string Name = \"{info.Name}\";");
        sb.AppendLine($"        /// <summary>Feature identifier</summary>");
        sb.AppendLine($"        public const string Id = \"{info.Id}\";");
        sb.AppendLine("    }");
        sb.AppendLine("}");
        return sb.ToString();
    }
}