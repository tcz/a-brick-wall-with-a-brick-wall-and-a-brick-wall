<?php

$dir = 'results';

// Get the list of files in the directory
$files = scandir($dir);

// Remove . and .. from the list
$files = array_diff($files, ['.', '..']);

// Sort the files alphabetically
sort($files, SORT_STRING);

// Get the last file from the sorted list
$lastFile = end($files);
$title = str_replace('_', ' ', substr($lastFile, 0, strlen($lastFile) - 4));

if (count($files))
$penultimateFile = $files[count($files) - 2];
$penultimateTitle = str_replace('_', ' ', substr($penultimateFile, 0, strlen($penultimateFile) - 4));

echo json_encode([
    'url' => $dir . '/' . $lastFile,
    'title' => $title,
    'lastTitle' => $penultimateTitle,
    'lastUrl' => $dir . '/' . $penultimateFile,
]);