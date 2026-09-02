// Polyfill for init-only setters in netstandard2.0
// (System.Runtime.CompilerServices.IsExternalInit was added in .NET 5)
namespace System.Runtime.CompilerServices
{
    internal static class IsExternalInit
    {
    }
}
