{ pkgs ? import <nixpkgs> {} }:

let
  python-env = pkgs.python3.withPackages (ps: with ps; [
    requests
    scapy 
    fastapi
  ]);
in
pkgs.mkShell {
  buildInputs = [
    python-env
    pkgs.libpcap
  ];

  shellHook = ''
    export LD_LIBRARY_PATH="${pkgs.libpcap}/lib:$LD_LIBRARY_PATH"
    
    echo "--- Nix Python Shell ---"
    echo "Python: $(python --version)"
  '';
}
