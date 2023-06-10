{ pkgs, ... }:

{
  packages = [ pkgs.git ];

  enterShell = ''
  '';

  languages.python = {
    enable = true;
    venv.enable = true;
    venv.requirements = ''
      build
      twine
    '';
  };
}
