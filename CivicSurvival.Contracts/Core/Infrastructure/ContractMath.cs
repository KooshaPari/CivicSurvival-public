namespace CivicSurvival.Core.Infrastructure;

/// <summary>Framework-neutral numeric helpers used by generated contracts.</summary>
public static class ContractMath
{
    public static float Clamp(float value, float min, float max)
        => value < min ? min : value > max ? max : value;

    public static int Clamp(int value, int min, int max)
        => value < min ? min : value > max ? max : value;
}
