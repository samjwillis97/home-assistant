{
  description = "Gleam project with extended neovim config";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    modular-neovim.url = "github:samjwillis97/modular-neovim-flake/extensive";
    modular-neovim.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs =
    {
      self,
      nixpkgs,
      modular-neovim,
      ...
    }:
    let
      system = "aarch64-darwin";
      pkgs = import nixpkgs {
        inherit system;
        config.allowBroken = true;
      };

      neovim = (
        modular-neovim.lib.${system}.extendModules [
          {
            custom.copilot.autocomplete.enable = true;
          }
          {
            plugins.conform-nvim.settings = {
              formatters_by_ft = {
                python = [ "autopep8" ];
              };

              formatters = {
                isort = {
                  command = "${pkgs.isort}/bin/isort";
                };
                autopep8 = {
                  command = "${pkgs.python313Packages.autopep8}/bin/autopep8";
                };
              };
            };

            plugins.lsp.servers.basedpyright = {
              enable = true;
            };
          }
        ]
      );
    in
    {
      devShells.${system} = {

        default = pkgs.mkShell {

          venvDir = "./.venv";

          packages = [
            neovim

            pkgs.python313Packages.venvShellHook
            pkgs.python313Packages.pip

            pkgs.ruff

            (pkgs.python3.withPackages (python-pkgs: with python-pkgs; [
              pyaudio
              numpy
              matplotlib
              scipy
              scipy-stubs
              tkinter
              aiohttp
            ]))
          ];
        };
      };
    };
}
