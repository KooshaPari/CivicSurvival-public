use std::{env, path::PathBuf, process::Command};

fn main() {
    let manifest_dir = PathBuf::from(env::var_os("CARGO_MANIFEST_DIR").expect("manifest dir"));
    let repo_root = manifest_dir.parent().and_then(|path| path.parent()).expect("native root");
    let schema = repo_root
        .join(".agileplus/civic-warfare-program/contracts/warfare.fbs");
    let out_dir = PathBuf::from(env::var_os("OUT_DIR").expect("out dir"));
    let flatc = env::var_os("CIVIC_FLATC").unwrap_or_else(|| "flatc".into());

    println!("cargo:rerun-if-changed={}", schema.display());
    let status = Command::new(flatc)
        .args(["--rust", "-o"])
        .arg(&out_dir)
        .arg(&schema)
        .status()
        .expect("flatc v25.12.19 is required to build civic-ffi");
    assert!(status.success(), "flatc failed while generating warfare bindings");
}
