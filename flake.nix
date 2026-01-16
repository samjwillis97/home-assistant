{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    git-hooks.url = "github:cachix/git-hooks.nix";
    git-hooks.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      git-hooks,
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

        # Pre-commit hooks configuration
        pre-commit-check = git-hooks.lib.${system}.run {
          src = ./.;
          hooks = {
            # YAML linting
            yamllint = {
              enable = true;
              name = "yamllint";
              entry = "${pkgs.yamllint}/bin/yamllint";
              files = "\\.(yaml|yml)$";
            };

            # Prettier formatting check
            prettier = {
              enable = true;
              name = "prettier";
              entry = "${pkgs.nodePackages.prettier}/bin/prettier --check";
              files = "\\.(yaml|yml)$";
            };

            # Home Assistant configuration validation
            home-assistant-config = {
              enable = true;
              name = "Home Assistant Config Check";
              entry = "${validate-ha-config}/bin/validate-ha-config";
              pass_filenames = false;
              files = "\\.(yaml|yml)$";
            };
          };
        };
      in
      with pkgs;
      {
        # Expose the pre-commit checks
        checks = {
          pre-commit = pre-commit-check;
        };

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
              ${pre-commit-check.shellHook}
              
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
