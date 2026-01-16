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

        # Wrapper script for running automation tests
        run-ha-tests = pkgs.writeShellScriptBin "run-ha-tests" ''
          exec pytest tests/ -v --cov --cov-report=term-missing
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
              stages = [ "pre-push" ];
            };

            # Automation logic tests
            pytest = {
              enable = false;
              name = "Automation Logic Tests";
              entry = "pytest tests/";
              pass_filenames = false;
              files = "\\.(py|yaml|yml)$";
              stages = [ "pre-push" ];
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

        # Expose apps for easy running
        apps = {
          test = {
            type = "app";
            program = "${run-ha-tests}/bin/run-ha-tests";
          };
          validate = {
            type = "app";
            program = "${validate-ha-config}/bin/validate-ha-config";
          };
        };

        # Expose packages
        packages = {
          run-ha-tests = run-ha-tests;
          validate-ha-config = validate-ha-config;
        };

        devShells = {
          default = mkShell {
            venvDir = "./.venv";

            packages = [
              pkgs.docker
              pkgs.python313
              pkgs.python313Packages.pip

              validate-ha-config
              run-ha-tests
            ];

            nativeBuildInputs = [
              pkgs.python313Packages.venvShellHook
            ];

            postVenvCreation = ''
              pip install -r requirements-test.txt
            '';

            postShellHook = ''
              ${pre-commit-check.shellHook}

              echo "🏠 Home Assistant Development Environment"
              echo ""
              echo "Available commands:"
              echo "  validate-ha-config - Validate Home Assistant configuration using Docker"
              echo "  run-ha-tests       - Run automation logic tests with pytest"
              echo ""
              echo "Testing shortcuts:"
              echo "  run-ha-tests                    - Run all tests with coverage"
              echo "  run-ha-tests tests/automations/ - Run specific test directory"
              echo "  run-ha-tests -k test_name       - Run tests matching pattern"
              echo ""
            '';
          };
        };
      }
    );
}
