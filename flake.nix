{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };

        # Wrapper script that calls the validation script
        validate-ha-config = pkgs.writeShellScriptBin "validate-ha-config" ''
          # Set PROJECT_ROOT for the script to use
          export PROJECT_ROOT="$(pwd)"
          exec ${pkgs.bash}/bin/bash ${./scripts/validate-config.sh} "$@"
        '';
      in
      with pkgs;
      {
        devShells = {
          default = mkShell {

            venvDir = "./.venv";

            packages = [
              pkgs.docker

              pkgs.python313Packages.venvShellHook
              pkgs.python313Packages.pip
              (pkgs.python3.withPackages (
                python-pkgs: with python-pkgs; [
                ]
              ))

              validate-ha-config
            ];

            shellHook = ''
              echo "🏠 Home Assistant Development Environment"
              echo ""
              echo "Available commands:"
              echo "  validate-ha-config - Validate Home Assistant configuration using Docker"
              echo ""
            '';
          };
        };
      }
    );
}
