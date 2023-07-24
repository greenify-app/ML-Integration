import 'package:flutter/material.dart';

import 'object_identification.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Greenify',
      home: object_identification(),
    );
  }
}
