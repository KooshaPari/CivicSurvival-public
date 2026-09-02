using System;

namespace CivicSurvival.Core.Attributes;

/// <summary>
/// Marks an interface as requiring a null object implementation.
/// The NullObjectGenerator will generate a Null{Name} class that implements this interface
/// with all members returning default values.
/// </summary>
[AttributeUsage(AttributeTargets.Interface, Inherited = false, AllowMultiple = false)]
public sealed class GenerateNullObjectAttribute : Attribute
{
}